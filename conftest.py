from pathlib import Path

import biomodels


def download_repressilator():
    file = Path("repressilator.sbml")
    if file.exists():
        return

    omex = biomodels.get_omex("BIOMD12")
    file.write_bytes(omex.master.read_bytes())


def setup_readme():
    with open("README.md") as readme, open("test_readme.txt", "w") as out:
        lines = iter(readme)
        for line in lines:
            if line.startswith("```python"):
                while not (line := next(lines)).startswith("```"):
                    if line == "time\n":
                        # Hardcoding whitespace in DataFrame output
                        # which is removed from README.md by pre-commit hooks
                        line = next(lines)
                        out.write("time")
                        out.write(" " * (len(line) - 5))
                        out.write("\n")
                    out.write(line)


download_repressilator()
setup_readme()
