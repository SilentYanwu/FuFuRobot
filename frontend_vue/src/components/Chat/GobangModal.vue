<template>
  <transition name="gobang-fade">
    <div v-if="visible" class="gobang-mask" @click.self="handleLeave">
      <div class="gobang-modal">
        <header class="modal-header">
          <div>
            <h3>五子棋对弈室</h3>
            <p v-if="triggerReason" class="trigger-reason">{{ triggerReason }}</p>
            <p class="status-text">{{ statusText }}</p>
          </div>
          <button class="leave-btn" type="button" @click="handleLeave">离席</button>
        </header>

        <section class="toolbar">
          <div class="level-group">
            <span class="label">芙芙水平</span>
            <button
              v-for="item in levelOptions"
              :key="item.value"
              type="button"
              class="level-btn"
              :class="{ active: level === item.value }"
              @click="level = item.value"
            >
              {{ item.label }}
            </button>
          </div>

          <div class="action-group">
            <button type="button" class="action-btn" @click="startNewGame">重开</button>
            <button type="button" class="action-btn" :disabled="!canUndo" @click="undoMove">
              悔棋
            </button>
          </div>
        </section>

        <section class="board-shell">
          <div class="board">
            <div v-for="row in rows" :key="`row-${row}`" class="board-row">
              <button
                v-for="col in cols"
                :key="`cell-${row}-${col}`"
                type="button"
                class="board-cell"
                :disabled="gameOver || isAiThinking || getCell(board, row, col) !== EMPTY"
                @click="handleCellClick(row, col)"
              >
                <span
                  v-if="getCell(board, row, col) !== EMPTY"
                  class="stone"
                  :class="getCell(board, row, col) === HUMAN ? 'black' : 'white'"
                ></span>
                <span v-if="isLastMove(row, col)" class="last-dot"></span>
              </button>
            </div>
          </div>
        </section>

        <p class="hint">你执黑子先手，点击“离席”可回到聊天。</p>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

type CellValue = 0 | 1 | 2
type Player = 1 | 2
type GobangLevel = 'expert' | 'normal' | 'newbie'

interface Move {
  row: number
  col: number
  player: Player
}

interface CandidateMove {
  row: number
  col: number
  score: number
}

interface LevelOption {
  value: GobangLevel
  label: string
}

interface Props {
  visible: boolean
  triggerReason?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const BOARD_SIZE = 15
const EMPTY: CellValue = 0
const HUMAN: Player = 1
const AI: Player = 2
const WIN_SCORE = 1_000_000
const DIRECTIONS: Array<[number, number]> = [
  [1, 0],
  [0, 1],
  [1, 1],
  [1, -1],
]

const level = ref<GobangLevel>('normal')
const board = ref<CellValue[][]>(createEmptyBoard())
const moveHistory = ref<Move[]>([])
const isAiThinking = ref(false)
const gameOver = ref(false)
const winner = ref<CellValue>(EMPTY)
const statusMessage = ref('准备开局，您执黑先行。')
const lastMove = ref<Move | null>(null)
let aiTimer: ReturnType<typeof setTimeout> | null = null

const rows = computed(() => Array.from({ length: BOARD_SIZE }, (_, index) => index))
const cols = computed(() => Array.from({ length: BOARD_SIZE }, (_, index) => index))
const canUndo = computed(() => moveHistory.value.length > 0 && !isAiThinking.value)

const levelOptions: LevelOption[] = [
  { value: 'expert', label: '高手' },
  { value: 'normal', label: '一般人' },
  { value: 'newbie', label: '菜鸟' },
]

const levelText = computed(() => {
  if (level.value === 'expert') return '高手'
  if (level.value === 'newbie') return '菜鸟'
  return '一般人'
})

const statusText = computed(() => {
  if (winner.value === HUMAN) return '恭喜你赢了这局。'
  if (winner.value === AI) return `芙芙（${levelText.value}）赢下这局。`
  if (gameOver.value) return '平局，棋盘已满。'
  if (isAiThinking.value) return `芙芙（${levelText.value}）正在思考...`
  return statusMessage.value
})

watch(
  () => props.visible,
  (isVisible) => {
    if (isVisible) {
      startNewGame()
    } else {
      stopAiTimer()
    }
  },
)

onBeforeUnmount(() => {
  stopAiTimer()
})

function createEmptyBoard(): CellValue[][] {
  return Array.from({ length: BOARD_SIZE }, () => Array.from({ length: BOARD_SIZE }, () => EMPTY))
}

function getCell(boardState: CellValue[][], row: number, col: number): CellValue {
  return boardState[row]?.[col] ?? EMPTY
}

function setCell(boardState: CellValue[][], row: number, col: number, value: CellValue) {
  const rowData = boardState[row]
  if (!rowData) return
  rowData[col] = value
}

function startNewGame() {
  stopAiTimer()
  board.value = createEmptyBoard()
  moveHistory.value = []
  isAiThinking.value = false
  gameOver.value = false
  winner.value = EMPTY
  statusMessage.value = '准备开局，您执黑先行。'
  lastMove.value = null
}

function handleLeave() {
  stopAiTimer()
  emit('close')
}

function stopAiTimer() {
  if (aiTimer) {
    clearTimeout(aiTimer)
    aiTimer = null
  }
  isAiThinking.value = false
}

function handleCellClick(row: number, col: number) {
  if (!props.visible || gameOver.value || isAiThinking.value) return
  if (getCell(board.value, row, col) !== EMPTY) return

  placeMove(row, col, HUMAN)

  if (checkWin(board.value, row, col, HUMAN)) {
    finishGame(HUMAN)
    return
  }

  if (isBoardFull(board.value)) {
    finishDraw()
    return
  }

  isAiThinking.value = true
  statusMessage.value = '芙芙正在落子...'
  aiTimer = setTimeout(() => {
    aiTimer = null
    runAiMove()
  }, 180)
}

function placeMove(row: number, col: number, player: Player) {
  setCell(board.value, row, col, player)
  const move: Move = { row, col, player }
  moveHistory.value.push(move)
  lastMove.value = move
}

function runAiMove() {
  if (gameOver.value) {
    isAiThinking.value = false
    return
  }

  const move = pickAiMove(board.value, level.value)
  if (!move) {
    finishDraw()
    isAiThinking.value = false
    return
  }

  placeMove(move.row, move.col, AI)

  if (checkWin(board.value, move.row, move.col, AI)) {
    finishGame(AI)
    return
  }

  if (isBoardFull(board.value)) {
    finishDraw()
    return
  }

  isAiThinking.value = false
  statusMessage.value = '轮到你落子。'
}

function finishGame(player: Player) {
  winner.value = player
  gameOver.value = true
  isAiThinking.value = false
}

function finishDraw() {
  gameOver.value = true
  winner.value = EMPTY
  isAiThinking.value = false
}

function undoMove() {
  if (!canUndo.value) return

  stopAiTimer()
  if (moveHistory.value.length === 0) return

  const latest = moveHistory.value[moveHistory.value.length - 1]
  if (!latest) return
  if (latest.player === AI && moveHistory.value.length >= 2) {
    rollbackOneMove()
    rollbackOneMove()
  } else {
    rollbackOneMove()
  }

  gameOver.value = false
  winner.value = EMPTY
  statusMessage.value = '已悔棋，轮到你重新落子。'
}

function rollbackOneMove() {
  const removed = moveHistory.value.pop()
  if (!removed) return

  setCell(board.value, removed.row, removed.col, EMPTY)
  lastMove.value =
    moveHistory.value.length > 0 ? (moveHistory.value[moveHistory.value.length - 1] ?? null) : null
}

function isLastMove(row: number, col: number) {
  return !!lastMove.value && lastMove.value.row === row && lastMove.value.col === col
}

function pickAiMove(boardState: CellValue[][], difficulty: GobangLevel): CandidateMove | null {
  const forcedMove = findForcedMove(boardState)

  if (difficulty === 'newbie') {
    return pickNewbieMove(boardState, forcedMove)
  }

  if (difficulty === 'normal') {
    return pickNormalMove(boardState, forcedMove)
  }

  return pickExpertMove(boardState, forcedMove)
}

function findForcedMove(boardState: CellValue[][]): CandidateMove | null {
  const candidates = getCandidateMoves(boardState, 40)

  for (const move of candidates) {
    if (wouldWin(boardState, move.row, move.col, AI)) {
      return { ...move, score: WIN_SCORE }
    }
  }

  for (const move of candidates) {
    if (wouldWin(boardState, move.row, move.col, HUMAN)) {
      return { ...move, score: WIN_SCORE - 1 }
    }
  }

  return null
}

function pickNewbieMove(
  boardState: CellValue[][],
  forcedMove: CandidateMove | null,
): CandidateMove | null {
  if (forcedMove) return forcedMove

  const candidates = getCandidateMoves(boardState, 30)
  if (candidates.length === 0) return null

  // 菜鸟：多数时候随机走，偶尔拿个高分点位防止过于离谱
  if (Math.random() < 0.28) {
    return candidates[0] ?? null
  }
  return candidates[Math.floor(Math.random() * candidates.length)] ?? null
}

function pickNormalMove(
  boardState: CellValue[][],
  forcedMove: CandidateMove | null,
): CandidateMove | null {
  if (forcedMove) return forcedMove

  const candidates = getCandidateMoves(boardState, 26)
  if (candidates.length === 0) return null

  const scored = candidates.map((move) => {
    const attack = scoreMovePotential(boardState, move.row, move.col, AI)
    const defense = scoreMovePotential(boardState, move.row, move.col, HUMAN)
    const centerBonus = 7 - Math.abs(move.row - 7) - Math.abs(move.col - 7)
    return {
      ...move,
      score: Math.max(attack * 1.05, defense * 1.1) + centerBonus,
    }
  })

  scored.sort((a, b) => b.score - a.score)
  return scored[0] ?? null
}

function pickExpertMove(
  boardState: CellValue[][],
  forcedMove: CandidateMove | null,
): CandidateMove | null {
  if (forcedMove) return forcedMove

  const candidates = getCandidateMoves(boardState, 14)
  if (candidates.length === 0) return null

  const firstCandidate = candidates[0]
  if (!firstCandidate) return null

  let bestMove = firstCandidate
  let bestScore = -Infinity
  let alpha = -Infinity
  const beta = Infinity
  const searchDepth = 2

  for (const move of candidates) {
    setCell(boardState, move.row, move.col, AI)

    let score: number
    if (checkWin(boardState, move.row, move.col, AI)) {
      score = WIN_SCORE
    } else {
      score = minimax(boardState, searchDepth - 1, alpha, beta, false)
    }

    setCell(boardState, move.row, move.col, EMPTY)

    if (score > bestScore) {
      bestScore = score
      bestMove = move
    }

    alpha = Math.max(alpha, bestScore)
  }

  return bestMove
}

function minimax(
  boardState: CellValue[][],
  depth: number,
  alpha: number,
  beta: number,
  maximizingAi: boolean,
): number {
  const candidates = getCandidateMoves(boardState, maximizingAi ? 10 : 9)
  if (depth === 0 || candidates.length === 0) {
    return evaluateBoard(boardState)
  }

  if (maximizingAi) {
    let value = -Infinity

    for (const move of candidates) {
      setCell(boardState, move.row, move.col, AI)
      const score = checkWin(boardState, move.row, move.col, AI)
        ? WIN_SCORE - (2 - depth) * 100
        : minimax(boardState, depth - 1, alpha, beta, false)
      setCell(boardState, move.row, move.col, EMPTY)

      value = Math.max(value, score)
      alpha = Math.max(alpha, value)
      if (alpha >= beta) break
    }

    return value
  }

  let value = Infinity
  for (const move of candidates) {
    setCell(boardState, move.row, move.col, HUMAN)
    const score = checkWin(boardState, move.row, move.col, HUMAN)
      ? -WIN_SCORE + (2 - depth) * 100
      : minimax(boardState, depth - 1, alpha, beta, true)
    setCell(boardState, move.row, move.col, EMPTY)

    value = Math.min(value, score)
    beta = Math.min(beta, value)
    if (beta <= alpha) break
  }

  return value
}

function evaluateBoard(boardState: CellValue[][]): number {
  const candidates = getCandidateMoves(boardState, 40)
  if (candidates.length === 0) return 0

  let aiBest = 0
  let aiSecond = 0
  let humanBest = 0
  let humanSecond = 0

  for (const move of candidates) {
    const aiScore = scoreMovePotential(boardState, move.row, move.col, AI)
    const humanScore = scoreMovePotential(boardState, move.row, move.col, HUMAN)

    if (aiScore > aiBest) {
      aiSecond = aiBest
      aiBest = aiScore
    } else if (aiScore > aiSecond) {
      aiSecond = aiScore
    }

    if (humanScore > humanBest) {
      humanSecond = humanBest
      humanBest = humanScore
    } else if (humanScore > humanSecond) {
      humanSecond = humanScore
    }
  }

  return aiBest * 1.25 + aiSecond * 0.8 - (humanBest * 1.35 + humanSecond * 0.75)
}

function getCandidateMoves(boardState: CellValue[][], limit = 20): CandidateMove[] {
  const filledCells: Array<[number, number]> = []

  for (let row = 0; row < BOARD_SIZE; row += 1) {
    for (let col = 0; col < BOARD_SIZE; col += 1) {
      if (getCell(boardState, row, col) !== EMPTY) {
        filledCells.push([row, col])
      }
    }
  }

  if (filledCells.length === 0) {
    return [{ row: 7, col: 7, score: 0 }]
  }

  const candidateMap = new Map<string, CandidateMove>()
  for (const [row, col] of filledCells) {
    for (let dr = -2; dr <= 2; dr += 1) {
      for (let dc = -2; dc <= 2; dc += 1) {
        if (dr === 0 && dc === 0) continue
        const nextRow = row + dr
        const nextCol = col + dc
        if (!inBounds(nextRow, nextCol) || getCell(boardState, nextRow, nextCol) !== EMPTY) continue

        const key = `${nextRow}-${nextCol}`
        if (candidateMap.has(key)) continue

        const attack = scoreMovePotential(boardState, nextRow, nextCol, AI)
        const defense = scoreMovePotential(boardState, nextRow, nextCol, HUMAN)
        const centerBonus = 7 - Math.abs(nextRow - 7) - Math.abs(nextCol - 7)
        candidateMap.set(key, {
          row: nextRow,
          col: nextCol,
          score: attack * 1.05 + defense * 0.95 + centerBonus,
        })
      }
    }
  }

  const candidates = Array.from(candidateMap.values()).sort((a, b) => b.score - a.score)
  if (candidates.length > 0) {
    return candidates.slice(0, limit)
  }

  const fallbackMove = findFirstEmpty(boardState)
  return fallbackMove ? [fallbackMove] : []
}

function findFirstEmpty(boardState: CellValue[][]): CandidateMove | null {
  for (let row = 0; row < BOARD_SIZE; row += 1) {
    for (let col = 0; col < BOARD_SIZE; col += 1) {
      if (getCell(boardState, row, col) === EMPTY) {
        return { row, col, score: 0 }
      }
    }
  }
  return null
}

function wouldWin(boardState: CellValue[][], row: number, col: number, player: Player): boolean {
  if (getCell(boardState, row, col) !== EMPTY) return false
  setCell(boardState, row, col, player)
  const win = checkWin(boardState, row, col, player)
  setCell(boardState, row, col, EMPTY)
  return win
}

function scoreMovePotential(
  boardState: CellValue[][],
  row: number,
  col: number,
  player: Player,
): number {
  if (getCell(boardState, row, col) !== EMPTY) return -Infinity
  setCell(boardState, row, col, player)

  let score = 0
  for (const [dx, dy] of DIRECTIONS) {
    score += evaluateLine(boardState, row, col, player, dx, dy)
  }

  setCell(boardState, row, col, EMPTY)
  return score
}

function evaluateLine(
  boardState: CellValue[][],
  row: number,
  col: number,
  player: Player,
  dx: number,
  dy: number,
): number {
  let count = 1
  let openEnds = 0

  let nextRow = row + dx
  let nextCol = col + dy
  while (inBounds(nextRow, nextCol) && getCell(boardState, nextRow, nextCol) === player) {
    count += 1
    nextRow += dx
    nextCol += dy
  }
  if (inBounds(nextRow, nextCol) && getCell(boardState, nextRow, nextCol) === EMPTY) {
    openEnds += 1
  }

  nextRow = row - dx
  nextCol = col - dy
  while (inBounds(nextRow, nextCol) && getCell(boardState, nextRow, nextCol) === player) {
    count += 1
    nextRow -= dx
    nextCol -= dy
  }
  if (inBounds(nextRow, nextCol) && getCell(boardState, nextRow, nextCol) === EMPTY) {
    openEnds += 1
  }

  return patternScore(count, openEnds)
}

function patternScore(count: number, openEnds: number): number {
  if (count >= 5) return 200000
  if (count === 4 && openEnds === 2) return 18000
  if (count === 4 && openEnds === 1) return 5500
  if (count === 3 && openEnds === 2) return 2200
  if (count === 3 && openEnds === 1) return 520
  if (count === 2 && openEnds === 2) return 220
  if (count === 2 && openEnds === 1) return 60
  if (count === 1 && openEnds === 2) return 12
  return 1
}

function checkWin(boardState: CellValue[][], row: number, col: number, player: Player): boolean {
  for (const [dx, dy] of DIRECTIONS) {
    const total =
      1 +
      countDirection(boardState, row, col, player, dx, dy) +
      countDirection(boardState, row, col, player, -dx, -dy)
    if (total >= 5) return true
  }
  return false
}

function countDirection(
  boardState: CellValue[][],
  row: number,
  col: number,
  player: Player,
  dx: number,
  dy: number,
): number {
  let count = 0
  let nextRow = row + dx
  let nextCol = col + dy

  while (inBounds(nextRow, nextCol) && getCell(boardState, nextRow, nextCol) === player) {
    count += 1
    nextRow += dx
    nextCol += dy
  }

  return count
}

function isBoardFull(boardState: CellValue[][]): boolean {
  return boardState.every((line) => line.every((cell) => cell !== EMPTY))
}

function inBounds(row: number, col: number): boolean {
  return row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE
}
</script>

<style scoped>
.gobang-mask {
  position: fixed;
  inset: 0;
  background: rgba(8, 15, 35, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2500;
  padding: 18px;
}

.gobang-modal {
  width: min(920px, 96vw);
  border-radius: 20px;
  background: linear-gradient(180deg, #f9fcff 0%, #ecf3ff 100%);
  border: 1px solid rgba(125, 150, 189, 0.35);
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.25);
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px 20px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
}

.modal-header h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
}

.trigger-reason {
  margin: 6px 0 0;
  font-size: 12px;
  color: #64748b;
}

.status-text {
  margin: 8px 0 0;
  color: #1d4ed8;
  font-size: 14px;
  font-weight: 600;
}

.leave-btn {
  border: 1px solid #dbe3f1;
  background: #fff;
  color: #334155;
  border-radius: 10px;
  min-width: 74px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 600;
}

.leave-btn:hover {
  background: #f8fafc;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.level-group,
.action-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  color: #334155;
  font-size: 14px;
  font-weight: 600;
}

.level-btn,
.action-btn {
  border: 1px solid #d4dceb;
  border-radius: 10px;
  background: #fff;
  color: #334155;
  padding: 7px 12px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.level-btn:hover,
.action-btn:hover:not(:disabled) {
  border-color: #9bb4df;
  background: #f0f6ff;
}

.level-btn.active {
  border-color: #3b82f6;
  background: #dbeafe;
  color: #1e3a8a;
}

.action-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.board-shell {
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.8) 0%, rgba(227, 238, 255, 0.8) 100%);
  padding: 12px;
  border: 1px solid rgba(153, 174, 206, 0.5);
}

.board {
  width: min(72vh, 100%);
  max-width: 620px;
  margin: 0 auto;
  aspect-ratio: 1 / 1;
  padding: 8px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f5d59f 0%, #ebc57f 100%);
  box-shadow: inset 0 0 0 1px rgba(122, 74, 13, 0.22);
}

.board-row {
  display: grid;
  grid-template-columns: repeat(15, minmax(0, 1fr));
}

.board-cell {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  border: 1px solid rgba(130, 82, 35, 0.38);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.board-cell:disabled {
  cursor: default;
}

.stone {
  width: 72%;
  height: 72%;
  border-radius: 50%;
  box-shadow:
    inset 0 0 0 1px rgba(15, 23, 42, 0.2),
    0 1px 2px rgba(15, 23, 42, 0.25);
}

.stone.black {
  background: radial-gradient(circle at 30% 30%, #52525b 0%, #18181b 65%, #09090b 100%);
}

.stone.white {
  background: radial-gradient(circle at 30% 30%, #ffffff 0%, #e2e8f0 62%, #cbd5e1 100%);
}

.last-dot {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ef4444;
}

.hint {
  margin: 0;
  color: #475569;
  font-size: 13px;
}

.gobang-fade-enter-active,
.gobang-fade-leave-active {
  transition: opacity 0.2s ease;
}

.gobang-fade-enter-from,
.gobang-fade-leave-to {
  opacity: 0;
}

@media (max-width: 880px) {
  .gobang-modal {
    padding: 14px;
  }

  .board {
    width: min(92vw, 560px);
  }

  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
