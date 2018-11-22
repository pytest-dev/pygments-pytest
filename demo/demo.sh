#!/usr/bin/env bash
set -euxo pipefail

verbose=(-v)

runtest() {
    test="$1"
    ansi_md="${test}_ansi.md"
    ansi_htm="${test}_ansi.htm"
    pytest_md="${test}_pytest.md"
    pytest_htm="${test}_pytest.htm"

    echo '```ansi' > "${ansi_md}"
    pytest "${verbose[@]}" --color=yes "${test}" >> "${ansi_md}" || true
    echo '```' >> "${ansi_md}"

    echo '```pytest' > "${pytest_md}"
    pytest "${verbose[@]}" "${test}" >> "${pytest_md}" || true
    echo '```' >> "${pytest_md}"

    markdown-code-blocks-highlight "${ansi_md}" > "${ansi_htm}"
    markdown-code-blocks-highlight "${pytest_md}" > "${pytest_htm}"
    sed \
        -i 's|<html>|<html><head><link rel="stylesheet" href="color.css"/></head>|g' \
        "${ansi_htm}" "${pytest_htm}"
}

runtest fail.py
runtest notests.py
runtest pass.py
runtest x.py
