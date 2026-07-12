#!/usr/bin/env bash
# ============================================================
#  convert_to_m4a.sh — AV3A/MP4 → AAC/M4A 批量转码
#
#  前置条件:
#    tools/av3a_decoder/av3a_decoder.exe  (已下载)
#    ffmpeg
#
#  流程:
#    MP4 → [提取 raw AV3A] → [av3a_decoder] → WAV → [ffmpeg+AAC] → M4A
#
#  用法:
#    ./convert_to_m4a.sh
#
#  并行: 自动检测 CPU 核心数，同时处理多个文件
#  设置环境变量覆盖: MAX_JOBS=2 ./convert_to_m4a.sh
# ============================================================
set -uo pipefail
# 注意: 不用 -e，因为 ((counter++)) 在 counter=0 时返回 1 会误触发退出

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/music"
OUTPUT_DIR="$SOURCE_DIR/m4a"
ORIGINALS_DIR="$SOURCE_DIR/originals"
DECODER="$SCRIPT_DIR/tools/av3a_decoder/av3a_decoder.exe"
EXTRACTOR_PY="$SCRIPT_DIR/tools/extract_av3a.py"

# ---------- 参数 ----------
AAC_BITRATE="256k"
OUTPUT_CHANNELS=2
# 并行数: 默认 CPU 核心数，可通过环境变量覆盖
MAX_JOBS="${MAX_JOBS:-$(python -c "import os; print(os.cpu_count())" 2>/dev/null || echo 4)}"
# ------------------------

red()    { printf "\033[31m%s\033[0m\n" "$*"; }
green()  { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

echo ""
green "========================================"
green "  AV3A(MP4) → AAC(M4A) 批量转码"
green "  并行数: $MAX_JOBS"
green "========================================"
echo ""

# --- 检查依赖 ---
if ! command -v ffmpeg &>/dev/null; then
    red "[错误] 找不到 ffmpeg。"
    exit 1
fi
echo "  [OK] ffmpeg"

if ! command -v python &>/dev/null; then
    red "[错误] 找不到 python。"
    exit 1
fi
echo "  [OK] python"

if [[ ! -f "$DECODER" ]]; then
    red "[错误] 找不到解码器: $DECODER"
    echo "  请从蓝奏云下载: https://wwp.lanzn.com/b05f4b0xe 密码: 6jj4"
    exit 1
fi
echo "  [OK] av3a_decoder"

# --- Python 提取脚本（内联写入） ---
mkdir -p "$(dirname "$EXTRACTOR_PY")"
cat > "$EXTRACTOR_PY" << 'PYEOF'
"""从 MP4 容器中提取 raw AV3A 流 (mdat box)"""
import struct, sys, os

def extract_mdat(filepath, outpath):
    with open(filepath, 'rb') as f:
        data = f.read()
    pos = 0
    while pos + 8 <= len(data):
        size, boxtype = struct.unpack('>I4s', data[pos:pos+8])
        name = boxtype.decode('ascii', errors='replace')
        if size == 1:
            size = struct.unpack('>Q', data[pos+8:pos+16])[0]
            hdr = 16
        elif size == 0:
            size = len(data) - pos
            hdr = 8
        else:
            hdr = 8
        if name == 'mdat':
            offset = pos + hdr
            length = size - hdr
            with open(outpath, 'wb') as out:
                out.write(data[offset:offset+length])
            return length
        pos += size
    raise RuntimeError(f"No mdat box found in {filepath}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.mp4> <output.av3a>")
        sys.exit(1)
    size = extract_mdat(sys.argv[1], sys.argv[2])
    print(f"Extracted {size} bytes")
PYEOF

# --- 检查源文件 ---
shopt -s nullglob
FILES=("$SOURCE_DIR"/*)
shopt -u nullglob

SOURCE_FILES=()
for f in "${FILES[@]}"; do
    if [[ -f "$f" ]]; then
        # 跳过 m4a 和 originals 子目录里的文件（避免重复处理）
        case "$f" in
            "$OUTPUT_DIR"/*|"$ORIGINALS_DIR"/*) continue ;;
        esac
        SOURCE_FILES+=("$f")
    fi
done

if [[ ${#SOURCE_FILES[@]} -eq 0 ]]; then
    yellow "[跳过] music/ 中没有可转换的文件。"
    yellow "  请把 AV3A/MP4 文件放到 music/ 目录"
    exit 0
fi

echo "  待处理: ${#SOURCE_FILES[@]} 个文件"
echo "  (解码较慢，约 30-50 分钟/文件，${MAX_JOBS} 个并行)"
echo ""

mkdir -p "$OUTPUT_DIR" "$ORIGINALS_DIR"

# ============================================================
# 单文件处理函数（在子 shell 中并行执行）
# ============================================================
process_file() {
    local src="$1"
    local STATUS_DIR="$2"
    local BASENAME NAME_NOEXT TMP_RAW TMP_WAV DST STATUS_FILE

    BASENAME="$(basename "$src")"
    NAME_NOEXT="${BASENAME%.*}"
    TMP_RAW="$OUTPUT_DIR/.tmp_${NAME_NOEXT}.av3a"
    TMP_WAV="$OUTPUT_DIR/.tmp_${NAME_NOEXT}.wav"
    DST="$OUTPUT_DIR/${NAME_NOEXT}.m4a"
    STATUS_FILE="$STATUS_DIR/${NAME_NOEXT}.status"

    # 所有输出重定向到临时日志，避免并行时交错乱码
    local LOGFILE="$STATUS_DIR/${NAME_NOEXT}.log"
    exec > >(tee -a "$LOGFILE") 2>&1

    echo "═══════════════════════════════════════════"
    echo "  [$BASENAME]  (PID $$)"
    echo ""

    if [[ -f "$DST" ]]; then
        yellow "  → 已存在，跳过。"
        echo "skipped" > "$STATUS_FILE"
        exit 0
    fi

    # Step 1: 提取 raw AV3A（快，~10 秒）
    echo -n "  [1/3] 提取 AV3A 流 ... "
    if python "$EXTRACTOR_PY" "$src" "$TMP_RAW" 2>&1; then
        green "OK"
    else
        red "FAIL"
        rm -f "$TMP_RAW"
        echo "failed" > "$STATUS_FILE"
        exit 1
    fi

    # Step 2: 解码 AV3A → WAV（慢，核心瓶颈）
    echo -n "  [2/3] 解码 → WAV (预计 30-50 分钟) ... "
    if "$DECODER" "$TMP_RAW" "$TMP_WAV" 2>&1; then
        green "OK"
        rm -f "$TMP_RAW"
    else
        red "FAIL"
        rm -f "$TMP_RAW" "$TMP_WAV"
        echo "failed" > "$STATUS_FILE"
        exit 1
    fi

    # Step 3: WAV → AAC/M4A + 从源文件注入元数据（快，~30 秒）
    echo -n "  [3/3] 编码 → M4A ... "
    if ffmpeg -y \
        -i "$TMP_WAV" \
        -i "$src" \
        -map 0:a \
        -map_metadata 1 \
        -ac "$OUTPUT_CHANNELS" \
        -c:a aac \
        -b:a "$AAC_BITRATE" \
        -movflags +faststart \
        -loglevel error -stats \
        "$DST" 2>&1; then
        green "    [OK] → $DST"
        rm -f "$TMP_WAV"
        # 移动源文件到 originals 归档
        mv "$src" "$ORIGINALS_DIR/"
        echo "  [归档] → $ORIGINALS_DIR/$BASENAME"
        echo "success" > "$STATUS_FILE"
    else
        red "    [FAIL]"
        rm -f "$TMP_WAV" "$DST"
        echo "failed" > "$STATUS_FILE"
        exit 1
    fi
}

# ============================================================
# 并行调度
# ============================================================
STATUS_DIR="$OUTPUT_DIR/.status_$$"
mkdir -p "$STATUS_DIR"

PIDS=()
JOB_INDEX=0

for src in "${SOURCE_FILES[@]}"; do
    # 控制并行数：达到 MAX_JOBS 时等待任意一个完成
    if [[ ${#PIDS[@]} -ge $MAX_JOBS ]]; then
        wait -n 2>/dev/null || true
        # 清理已完成的 PID
        NEW_PIDS=()
        for pid in "${PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                NEW_PIDS+=("$pid")
            fi
        done
        PIDS=("${NEW_PIDS[@]}")
    fi

    process_file "$src" "$STATUS_DIR" &
    PIDS+=($!)
    ((JOB_INDEX++))
done

# 等待所有任务完成
echo ""
echo "  等待所有任务完成..."
for pid in "${PIDS[@]}"; do
    wait "$pid" 2>/dev/null || true
done

# ============================================================
# 汇总结果
# ============================================================
SUCCESS=0; SKIPPED=0; FAILED=0

for sf in "$STATUS_DIR"/*.status; do
    [[ -f "$sf" ]] || continue
    case "$(cat "$sf")" in
        success) ((SUCCESS++)) ;;
        skipped) ((SKIPPED++)) ;;
        failed)  ((FAILED++)) ;;
    esac
done

# 合并日志
for lf in "$STATUS_DIR"/*.log; do
    [[ -f "$lf" ]] || continue
    cat "$lf"
done

# 清理状态目录
rm -rf "$STATUS_DIR"

echo ""
green "========================================"
echo "  完成: 成功 $SUCCESS / 跳过 $SKIPPED / 失败 $FAILED"
green "========================================"
[[ $SUCCESS -gt 0 ]] && echo "  输出: $OUTPUT_DIR"
[[ $SUCCESS -gt 0 ]] && echo "  归档: $ORIGINALS_DIR"

    # 自动通知服务器扫描新文件
    if [[ $SUCCESS -gt 0 ]]; then
        API_PORT="${API_PORT:-8080}"
        if command -v curl &>/dev/null; then
            curl -s -X POST "http://localhost:${API_PORT}/api/scan" > /dev/null 2>&1 || true
        fi
    fi
