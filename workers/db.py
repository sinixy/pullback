import time
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379)
script = """-- delete_old_entries.lua

local streams = redis.call('KEYS', '*USDT')
local now = redis.call('TIME')[1]
local min_id = tostring((now - 60)*1000) .. '-0'

for _, stream_key in ipairs(streams) do
    redis.call('XTRIM', stream_key, 'MINID', min_id)
end
"""

clean_script = r.register_script(script)

def clean():
    clean_script()
