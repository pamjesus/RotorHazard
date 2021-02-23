#ifndef PERSISTENT_HOMOLOGY_H
#define PERSISTENT_HOMOLOGY_H
#include "rhtypes.h"
#include "Collections.h"

struct ConnectedComponent {
    uint8_t birth;
    uint8_t death;
};

template <size_t N> static uint8_t findNextSmallest(List<Extremum,N>& pns, ExtremumType firstType, const rssi_t rssiLimit, const uint8_t lastIdx) {
    uint8_t nextIdx = 0xFF;
    rssi_t nextRssi = 0;
    ExtremumType nextType = NONE;

    ExtremumType t = firstType;
    for (uint8_t i=0; i<pns.size(); i++) {
        const rssi_t rssi = pns[i].rssi;
        if (rssi >= nextRssi && (rssi < rssiLimit || (rssi == rssiLimit && i < lastIdx))) {
            nextRssi = rssi;
            nextIdx = i;
            nextType = t;
        }
        t = (t == PEAK) ? NADIR : PEAK;
    }

    uint8_t typeBit = (nextType == PEAK) ? 1 : 0;
    return (nextIdx<<1) | typeBit; // bit packing - using LSB for extremum type
}

template <size_t N> static uint8_t findNextLargest(List<Extremum,N>& pns, ExtremumType firstType, const rssi_t rssiLimit, const uint8_t lastIdx) {
    uint8_t nextIdx = 0xFF;
    rssi_t nextRssi = MAX_RSSI;
    ExtremumType nextType = NONE;

    ExtremumType t = firstType;
    for (uint8_t i=0; i<pns.size(); i++) {
        const rssi_t rssi = pns[i].rssi;
        if (rssi <= nextRssi && (rssi > rssiLimit || (rssi == rssiLimit && i < lastIdx))) {
            nextRssi = rssi;
            nextIdx = i;
            nextType = t;
        }
        t = (t == PEAK) ? NADIR : PEAK;
    }

    uint8_t typeBit = (nextType == PEAK) ? 1 : 0;
    return (nextIdx<<1) | typeBit; // bit packing - using LSB for extremum type
}

template <size_t N> size_t calculatePeakPersistentHomology(List<Extremum,N>& pns, ExtremumType firstType, ConnectedComponent ccs[]) {
    int8_t idxToCC[N];
    static_assert(N <= 127, "can't exceed 127 due to bit packing");
    const uint8_t size = pns.size();

    uint8_t minIdx = 0xFF;
    rssi_t minRssi = MAX_RSSI;
    for (uint8_t i=0; i<size; i++) {
        idxToCC[i] = -1; // bit packing - using MSB for set/not set
        const rssi_t rssi = pns[i].rssi;
        if (rssi < minRssi) {
            minRssi = rssi;
            minIdx = i;
        }
    }

    uint8_t ccCount = 0;
    minRssi = MAX_RSSI;
    uint8_t idx = 0xFF;
    for (uint8_t i=0; i<size; i++) {
        const uint8_t typedIdx = findNextSmallest(pns, firstType, minRssi, idx);
        idx = typedIdx >> 1;
        minRssi = pns[idx].rssi;
        if (typedIdx&1) {
            // peak
            ConnectedComponent& cc = ccs[ccCount];
            cc.birth = idx;
            cc.death = minIdx;
            idxToCC[idx] = ccCount;
            ccCount++;
        } else {
            // nadir
            int8_t leftCCIdx = (idx > 0) ? idxToCC[idx-1] : -1;
            int8_t rightCCIdx = (idx < size-1) ? idxToCC[idx+1] : -1;
            if (leftCCIdx != -1 && rightCCIdx != -1) {
                ConnectedComponent& leftCC = ccs[leftCCIdx];
                ConnectedComponent& rightCC = ccs[rightCCIdx];
                if (pns[leftCC.birth].rssi > pns[rightCC.birth].rssi) {
                    // merge right into left
                    rightCC.death = idx;
                    idxToCC[idx+1] = idxToCC[idx-1];
                } else {
                    // merge left into right
                    leftCC.death = idx;
                    idxToCC[idx-1] = idxToCC[idx+1];
                }
            }
        }
    }
    return ccCount;
}

template <size_t N> size_t calculateNadirPersistentHomology(List<Extremum,N>& pns, ExtremumType firstType, ConnectedComponent ccs[]) {
    int8_t idxToCC[N];
    static_assert(N <= 127, "can't exceed 127 due to bit packing");
    const uint8_t size = pns.size();

    uint8_t maxIdx = 0xFF;
    rssi_t maxRssi = 0;
    for (uint8_t i=0; i<size; i++) {
        idxToCC[i] = -1; // bit packing - using MSB for set/not set
        const rssi_t rssi = pns[i].rssi;
        if (rssi > maxRssi) {
            maxRssi = rssi;
            maxIdx = i;
        }
    }

    uint8_t ccCount = 0;
    maxRssi = 0;
    uint8_t idx = 0xFF;
    for (uint8_t i=0; i<size; i++) {
        const uint8_t typedIdx = findNextLargest(pns, firstType, maxRssi, idx);
        idx = typedIdx >> 1;
        maxRssi = pns[idx].rssi;
        if (typedIdx&1) {
            // peak
            int8_t leftCCIdx = (idx > 0) ? idxToCC[idx-1] : -1;
            int8_t rightCCIdx = (idx < size-1) ? idxToCC[idx+1] : -1;
            if (leftCCIdx != -1 && rightCCIdx != -1) {
                ConnectedComponent& leftCC = ccs[leftCCIdx];
                ConnectedComponent& rightCC = ccs[rightCCIdx];
                if (pns[leftCC.birth].rssi < pns[rightCC.birth].rssi) {
                    // merge right into left
                    rightCC.death = idx;
                    idxToCC[idx+1] = idxToCC[idx-1];
                } else {
                    // merge left into right
                    leftCC.death = idx;
                    idxToCC[idx-1] = idxToCC[idx+1];
                }
            }
        } else {
            // nadir
            ConnectedComponent& cc = ccs[ccCount];
            cc.birth = idx;
            cc.death = maxIdx;
            idxToCC[idx] = ccCount;
            ccCount++;
        }
    }
    return ccCount;
}
#endif
