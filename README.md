# ACAD wrapping example

This repo contains classes for easy connection to running ACAD application via win32com.client

## Description

The goal is to build electrical scheme from pre-designed blocks and specification

Q: What schemes could be builded by this module?
A: Schemes, contained replicated blocks. Example: PLC in/outs connections scheme.

You can specify PLC processor and modules structure, wrap them in PLCModule Class instances and generate scheme out of specification.

1. Specification must contain wire labels
2. Specification must contain type of connection (DIN/DOT/AIN/AOT)
3. Every connection is PLC contact to clemm connection

## Usage case

This script was developed to automate electrical scheme design with reccuring scheme blocks.
