-- Step runner for platforms/ps1/redux.py: runs inside PCSX-Redux (-cli -interpreter -debugger).
-- Reads the step lines from KIT_STEPS (a file), writes results under KIT_OUT, prints "@@ ..." lines.
-- Steps are described in redux.py. The emulator runs only during waits; between steps it is paused,
-- so peeks, registers and dumps are exact.
local ffi = require('ffi')
local STEPS, OUT = os.getenv('KIT_STEPS'), os.getenv('KIT_OUT') or '.'
local STATES = os.getenv('KIT_STATES') or (OUT .. '/states')
local B = PCSX.CONSTS.PAD.BUTTON
local pad = PCSX.SIO0.slots[1].pads[1]
local BUTTON = { CROSS = B.CROSS, A = B.CROSS, CIRCLE = B.CIRCLE, B = B.CIRCLE, SQUARE = B.SQUARE, TRIANGLE = B.TRIANGLE,
  L1 = B.L1, R1 = B.R1, L2 = B.L2, R2 = B.R2, START = B.START, SELECT = B.SELECT,
  UP = B.UP, DOWN = B.DOWN, LEFT = B.LEFT, RIGHT = B.RIGHT }
local REGS = { 'r0', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
  's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 's8', 'ra', 'lo', 'hi' }

local frame = 0
local advance                                     -- defined below
local mem = PCSX.getMemPtr()                     -- main RAM, 2 MB, uint8_t*
local breaks, hit = {}, nil

local function say(...) print('@@ ' .. string.format(...)); io.stdout:flush() end
local function die(msg) say('ERROR %s', msg); io.stdout:flush(); PCSX.quit(1); error(msg, 0) end
local function num(s)                            -- decimal, or $xx / 0x..
  if s:sub(1, 1) == '$' then return tonumber(s:sub(2), 16) end
  return tonumber(s)
end
local function addr(s)                           -- hex CPU address; KSEG bits ignored
  s = s:gsub('^%$', ''):gsub('^0[xX]', '')
  return tonumber(s, 16)
end
local function off(a, n)
  local o = a % 0x20000000
  if o + n > 0x200000 then die(string.format('%08X+%d is not main RAM', a, n)) end
  return o
end
local function writefile(path, data)
  local f = assert(io.open(path, 'wb')); f:write(data); f:close()
end
local function split(line) local t = {}; for w in line:gmatch('%S+') do t[#t + 1] = w end; return t end

-- ---- breakpoints: a hit pauses the emulator and ends the current wait
local function onhit(kind, a, w, cause)
  if hit then return end
  local r = PCSX.getRegisters()
  hit = { kind = kind, addr = a, pc = r.pc, frame = frame }
  PCSX.pauseEmulator()
  if advance then advance() end                   -- nextTick is not serviced while paused: carry on from here
end

-- ---- screenshots: raw file + meta; redux.py turns them into PNGs
local function saveshot(name, ss_data, w, h, bpp)
  writefile(OUT .. '/' .. name .. '.raw', ss_data)
  writefile(OUT .. '/' .. name .. '.meta', string.format('%d %d %d\n', w, h, bpp))
end

-- ---- the steps (each returns nil, or a number of frames to run, or 'run' to run until a break)
local steps = {}
local function hold(btns, frames)
  for b in btns:upper():gmatch('[^+]+') do
    if not BUTTON[b] then die('unknown button ' .. b) end
    pad.setOverride(BUTTON[b])
  end
end
local function release(btns)
  for b in btns:upper():gmatch('[^+]+') do pad.clearOverride(BUTTON[b]) end
end

local queue = {}                                 -- micro-steps injected by press / mash
local function push(f) queue[#queue + 1] = f end

function steps.wait(a) return num(a[2]) end
function steps.press(a)
  local k, n = 1, num(a[3] or '4') or 4
  local last = a[#a]
  if #a >= 3 and last:match('^[xX]%d+$') then k = tonumber(last:sub(2)); if #a == 3 then n = 4 end end
  for _ = 1, k do
    push(function() hold(a[2]) return n end)
    push(function() release(a[2]) return 12 end)
  end
end
function steps.mash(a)
  local frames, every = num(a[3]), num(a[4] or '12')
  for _ = 1, math.max(1, math.floor(frames / every)) do
    push(function() hold(a[2]) return 4 end)
    push(function() release(a[2]) return math.max(0, every - 4) end)
  end
end
function steps.shot(a)
  local ss = PCSX.GPU.takeScreenShot()
  local bpp = (tostring(ss.bpp):find('24') or tostring(ss.bpp):find(': 1')) and 24 or 16
  saveshot(a[2], ffi.string(ss.data.data, ss.data.size), ss.width, ss.height, bpp)
  say('shot %s %dx%d', a[2], ss.width, ss.height)
end
function steps.vshot(a)                          -- vshot NAME X Y W H [24]: a rectangle of VRAM (units: 16-bit pixels)
  local x, y, w, h = num(a[3]), num(a[4]), num(a[5]), num(a[6])
  local bpp = (a[7] == '24') and 24 or 16
  local v = PCSX.GPU.getVRAM()
  local vram = ffi.cast('uint8_t*', v.data)
  local rows = {}
  local rowbytes = (bpp == 24) and w * 3 or w * 2
  for r = 0, h - 1 do rows[#rows + 1] = ffi.string(vram + ((y + r) * 1024 + x) * 2, rowbytes) end
  saveshot(a[2], table.concat(rows), w, h, bpp)
  say('vshot %s %dx%d @%d,%d', a[2], w, h, x, y)
end
function steps.vram(a)
  local v = PCSX.GPU.getVRAM()
  writefile(OUT .. '/' .. a[2] .. '.bin', ffi.string(v.data, v.size))
  say('vram %s %d bytes', a[2], v.size)
end
function steps.peek(a)
  local n = num(a[3] or '1')
  local o = off(addr(a[2]), n)
  local t = {}
  for i = 0, n - 1 do t[#t + 1] = string.format('%02x', mem[o + i]) end
  local text = string.format('peek %08X: %s', addr(a[2]), table.concat(t, ' '))
  say('%s', text)
  local f = io.open(OUT .. '/peek.txt', 'a'); f:write(text .. '\n'); f:close()
end
function steps.poke(a)
  local bytes = table.concat(a, ',', 3)
  local o, n = off(addr(a[2]), 1), 0
  for v in bytes:gmatch('[^,]+') do mem[o + n] = num(v) % 256; n = n + 1 end
  off(addr(a[2]), n)
end
function steps.dump(a)                           -- dump ram START LEN NAME
  if a[2]:lower() ~= 'ram' then die('dump: region must be ram (or use vram)') end
  local start, n = addr(a[3]), num(a[4])
  writefile(OUT .. '/' .. a[5] .. '.bin', ffi.string(mem + off(start, n), n))
end
function steps.save(a)
  local f = a[2]:match('%.state$') and a[2] or (STATES .. '/' .. a[2] .. '.state')
  os.execute('mkdir -p "' .. f:match('^(.*)/[^/]*$') .. '"')
  local s = PCSX.createSaveState()
  writefile(f, ffi.string(s.data, s.size))
end
function steps.load(a)
  local f = a[2]:match('%.state$') and a[2] or (STATES .. '/' .. a[2] .. '.state')
  if not io.open(f, 'rb') then die('no savestate ' .. f) end
  PCSX.loadSaveState(Support.File.open(f))
  return 2
end
function steps.reg(a)                            -- reg NAME [VALUE]
  local r = PCSX.getRegisters()
  local name = a[2]:lower()
  if name == 'zero' then name = 'r0' elseif name == 'fp' then name = 's8' end
  if a[3] then
    if name == 'pc' then r.pc = num(a[3]) else r.GPR.n[name] = num(a[3]) end
  end
  local v = (name == 'pc') and r.pc or r.GPR.n[name]
  say('reg %s = %08x', name, v)
end
function steps.regs(a)
  local r = PCSX.getRegisters()
  local out = { string.format('pc=%08x', r.pc) }
  for _, n in ipairs(REGS) do
    local ok, v = pcall(function() return r.GPR.n[n] end)
    out[#out + 1] = string.format('%s=%s', n, ok and string.format('%08x', v) or '?')
  end
  say('regs %s', table.concat(out, ' '))
end
function steps.break_(a)                         -- break exec|read|write ADDR [LEN]
  local kind = ({ exec = 'Exec', read = 'Read', write = 'Write' })[a[2]:lower()]
  if not kind then die('break: exec, read or write') end
  local ad, w = addr(a[3]), num(a[4] or '4')
  breaks[#breaks + 1] = PCSX.addBreakpoint(ad, kind, w, 'kit', function(x, ww, c) onhit(kind, x, ww, c) end)
  say('break %s %08X (%d)', kind, ad, w)
end
steps['break'] = steps.break_
function steps.clear(a)
  for _, b in ipairs(breaks) do pcall(function() b:remove() end) end
  breaks, hit = {}, nil
end
function steps.run(a) return 'run', num(a[2] or '600') end
function steps.until_(a)                         -- until ADDR BYTE [LIMIT]
  local o, want, limit = off(addr(a[2]), 1), num(a[3]), num(a[4] or '600')
  return 'until', { o = o, want = want, limit = limit, at = a[2] }
end
steps['until'] = steps.until_

-- ---- the scheduler: one step at a time; waits run the emulator
local lines = {}
for l in io.lines(STEPS) do
  l = l:gsub('#.*$', ''):match('^%s*(.-)%s*$')
  if l ~= '' then lines[#lines + 1] = l end
end
local li = 0
local wait = nil                                  -- { kind='frames', stop=N } | { kind='run', stop=N } | { kind='until', ... }


local function finish()
  say('done frame=%d', frame)
  io.stdout:flush()
  PCSX.quit(0)
end

local function nextstep()
  if #queue > 0 then
    local f = table.remove(queue, 1)
    local n = f()
    return n
  end
  li = li + 1
  if li > #lines then return 'end' end
  local a = split(lines[li])
  local fn = steps[a[1]:lower()]
  if not fn then die('unknown step ' .. lines[li]) end
  local ok, r, extra = pcall(fn, a)
  if not ok then die(string.format('step %q: %s', lines[li], tostring(r))) end
  return r, extra
end

local function over()
  if not wait then return true end
  if hit then
    say('BREAK %s at %08X pc=%08x frame=%d', hit.kind, hit.addr, hit.pc, hit.frame)
    return true
  end
  if wait.kind == 'until' and mem[wait.o] == wait.want then return true end
  if frame >= wait.stop then
    if wait.kind == 'run' then say('run: no break in %d frames', wait.frames)
    elseif wait.kind == 'until' then say('until %s %d: not reached', wait.at, wait.want) end
    return true
  end
  return false
end

local running = false
function advance()
  if running then return end                     -- a break while steps are executing: they are paused anyway
  running = true
  local ok, err = pcall(function()
    if wait then
      if not over() then return end
      PCSX.pauseEmulator()
      wait, hit = nil, nil
    end
    while true do
      local r, extra = nextstep()
      if r == 'end' then return finish() end
      if r == 'run' then
        wait = { kind = 'run', stop = frame + extra, frames = extra }
      elseif r == 'until' then
        wait = { kind = 'until', stop = frame + extra.limit, o = extra.o, want = extra.want, at = extra.at }
      elseif type(r) == 'number' and r > 0 then
        wait = { kind = 'frames', stop = frame + r }
      end
      if wait then hit = nil; PCSX.resumeEmulator(); return end
    end
  end)
  running = false
  if not ok then die(tostring(err)) end
end

PCSX.Events.createEventListener('GPU::Vsync', function()
  frame = frame + 1
  if frame % 300 == 0 then print('@@~ ' .. frame); io.stdout:flush() end   -- heartbeat for redux.py's stall check
  if wait and not hit then advance() end
end)

PCSX.settings.spu.Speed = tonumber(os.getenv('KIT_SPEED') or '20')
os.execute('mkdir -p "' .. OUT .. '"')
PCSX.pauseEmulator()
PCSX.nextTick(advance)
