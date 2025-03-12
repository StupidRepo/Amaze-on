package utils

import (
	"crypto/sha1"
	"encoding/hex"
)

var fixedKey = []byte{
	0x77, 0x21, 0x4d, 0x4b, 0x19, 0x6a, 0x87, 0xcd,
	0x52, 0x00, 0x45, 0xfd, 0x20, 0xa5, 0x1d, 0x67,
}

func hashData(data []byte) []byte {
	h := sha1.New()
	h.Write(data)

	return h.Sum(nil)
}

func CalculateChecksum(activationHex string) (string, error) {
	data, err := hex.DecodeString(activationHex)
	if err != nil {
		return "", err
	}

	intermediateKey := hashData(append(fixedKey, data...))
	intermediateIv := hashData(append(append(fixedKey, intermediateKey...), data...))
	combined := append(intermediateKey[:16], intermediateIv[:16]...)

	checksum := hashData(combined)
	checksumHex := hex.EncodeToString(checksum)

	return checksumHex, nil
}
