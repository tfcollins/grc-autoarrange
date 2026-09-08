#!/usr/bin/env node
/**
 * Standalone ELK Layout Runner
 * Reads an ELK JSON graph from stdin, executes ELK layout, and prints the result JSON to stdout.
 */

const path = require('path');
const ELK = require(path.join(__dirname, 'elk.bundled.js'));
const elk = new ELK();

let inputData = '';

process.stdin.setEncoding('utf8');

process.stdin.on('data', (chunk) => {
    inputData += chunk;
});

process.stdin.on('end', () => {
    if (!inputData.trim()) {
        process.stderr.write('Error: No input data received on stdin\n');
        process.exit(1);
    }

    let graph;
    try {
        graph = JSON.parse(inputData);
    } catch (err) {
        process.stderr.write(`Error parsing input JSON: ${err.message}\n`);
        process.exit(1);
    }

    elk.layout(graph)
        .then((result) => {
            process.stdout.write(JSON.stringify(result));
            process.exit(0);
        })
        .catch((err) => {
            process.stderr.write(`ELK layout error: ${err.message || err}\n`);
            process.exit(1);
        });
});
