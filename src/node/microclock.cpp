#include "config.h"
#include "microclock.h"

MicroClock usclock;

uint32_t MicroClock::tick()
{
    utime_t currentTick = micros();
    // unsigned arithmetic to handle roll-over
    uint32_t elapsed = currentTick - prevTick;
    uint32_t elapsedMillis = (elapsed + excessMicros)/1000;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
    {
        timeMillis += elapsedMillis;
        excessMicros = elapsed - elapsedMillis*1000;
    }
    prevTick = currentTick;
    return elapsed;
}

mtime_t MicroClock::millis()
{
    return timeMillis;
}