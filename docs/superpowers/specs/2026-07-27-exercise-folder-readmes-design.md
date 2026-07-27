# Exercise Folder Cleanup and README Design

## Goal

Make the `03_04_exercise_qaoa_and_adapt` folder a clean copy of the relevant
workshop files from
`/home/mawolf/vibeshop-cudaq/03_04_qaoa_and_adapt_qaoa`, and provide brief
file-orientation READMEs for exercises 02 and 03/04.

The separate workshop handout contains the exercises. The READMEs will not
repeat instructions, workflows, commands, or prerequisites.

## Final `03_04` Contents

The folder will contain only:

- `README.md`
- `adapt_qaoa.py`
- `qaoa_maxcut.py`
- `qaoa_maxcut_solvers.py`
- `workshop_graphs.py`
- `tests/test_qaoa_maxcut.py`

The five Python files will match their source files byte-for-byte. Generated
caches and the source folder's other tests will not be copied. All legacy
files and directories currently in the destination will be removed.

## README Format

Each README will contain:

1. A short title.
2. One sentence stating that the workshop handout provides the exercises.
3. A compact table listing every Python file currently in the folder and its
   purpose.

The exercise 02 README will describe its six existing Python files. The
exercise 03/04 README will describe the five Python files in its final
manifest, including the retained test.

## Verification

- Compare each transferred 03/04 Python file with its source.
- Confirm the 03/04 file manifest contains only the six approved paths.
- Confirm each README lists every Python file present in its exercise folder.
- Confirm no generated cache files are left behind.
