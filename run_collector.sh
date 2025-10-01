#!/bin/bash
# Remplace par les team IDs que tu veux collecter
TEAMS=(2817 5421)
for t in "${TEAMS[@]}"; do
  echo "Collecte pour team $t"
  python3 collector.py $t 100
done
