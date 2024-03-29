#!/bin/sh
if [ -z "$1" ]; then
    echo "Error: You must specify a full path to a cs file as the first parameter, then an output directory."
    exit 1
fi
prev_path="`pwd`"
tree="`realpath $1`"
dest="$2"
if [ -z "$dest" ]; then
    echo "Error: You must specify an output directory."
    exit 1
fi
if [ ! -d "$dest" ]; then
    echo "Error: You must specify an existing output directory."
    exit 1
fi
# cs2py_vendor=shannoncruey
cs2py_vendor=poikilos
cs2py_git="https://github.com/$cs2py_vendor/csharp-to-python.git"
REPOS=~/Downloads/git
cs2py_name="csharp-to-python"
vendor_repos=$REPOS/$cs2py_vendor
cs2py_repo=$vendor_repos/$cs2py_name
printf "* checking for $cs2py_name..."
if [ ! -d $cs2py_repo ]; then
    mkdir -p "$vendor_repos"
    cd "$vendor_repos"
    if [ $? -ne 0 ]; then
        echo "Error: 'cd \"$vendor_repos\"' failed."
        exit 1
    fi
    printf "downloading to \"$cs2py_repo\"..."
    git clone "$cs2py_git" "$cs2py_repo"
    if [ $? -ne 0 ]; then
        echo "Error: 'git clone \"$cs2py_git\" \"$cs2py_repo\"' failed in `pwd`."
        exit 1
    fi
    cd "$cs2py_repo"
    if [ $? -ne 0 ]; then
        echo "Error: 'cd \"$cs2py_repo\"' failed."
        exit 1
    fi
else
    cd "$cs2py_repo"
    if [ $? -ne 0 ]; then
        echo "Error: 'cd \"$cs2py_repo\"' failed."
        exit 1
    fi
    git pull
    if [ $? -ne 0 ]; then
        echo "Warning: 'git pull' failed in \"`pwd`\"."
        exit 1
    fi
fi
echo "OK"

cat > /dev/null <<END
target_msg="each file of $tree"
if [ -f $tree ]; then
    target_msg="$tree"
elif [ ! -d $tree ]; then
    echo "Error: \"$tree\" is neither a file nor a directory."
    exit 1
fi
echo "* Next, 'cd $cs2py_repo' then copy $target_msg to $cs2py_repo/convert.in and run:"
echo "  python3 convert.py aspx"
echo "  * then copy convert.out to the target python file you want to save."
END

cd "$prev_path"
CS2PYTHON=cs2python
if [ ! -f "`command -v cs2python`" ]; then
    if [ ! -d "../pycodetool" ]; then
        echo "Error: $cs2py_repo was installed, but pycodetool couldn't be found so you should use:"
        echo "pycodetool/cs2python \"$1\" \"$2\""
        echo "# ^ but change pycodetool to the correct location."
        exit 1
    else
        CS2PYTHON="../pycodetool/cs2python"
    fi
fi
echo "Running $CS2PYTHON \"$tree\" \"$dest\" --converter \"$cs2py_repo/convert.py\""
python3 $CS2PYTHON "$tree" "$dest" --converter "$cs2py_repo/convert.py"

exit $?

cat > /dev/null <<END
echo "FizzerWL's C# to HAXE converter requires C# and is only known to compile in an IDE."
cs2hx_git=https://github.com/FizzerWL/Cs2hx.git
REPOS=~/Downloads/git
FizzerWL_REPOS=$REPOS/FizzerWL/Cs2hx
cs2hx_repo=$FizzerWL_REPOS/Cs2hx
if [ ! -d $cs2hx_repo ]; then
    mkdir -p "$FizzerWL_REPOS"
    cd "$FizzerWL_REPOS"
    if [ $? -ne 0 ]; then
        echo "Error: 'cd \"$FizzerWL_REPOS\"' failed."
        exit 1
    fi
    git clone "$cs2hx_git" "$cs2hx_repo"
    if [ $? -ne 0 ]; then
        echo "Error: 'git clone \"$cs2hx_git\" \"$cs2hx_repo\"' failed in `pwd`."
        exit 1
    fi
    cd "$cs2hx_repo"
    if [ $? -ne 0 ]; then
        echo "Error: 'cd \"$cs2hx_repo\"' failed."
        exit 1
    fi
else
    cd "$cs2hx_repo"
    if [ $? -ne 0 ]; then
        echo "Error: 'cd \"$cs2hx_repo\"' failed."
        exit 1
    fi
    git pull
    if [ $? -ne 0 ]; then
        echo "Warning: 'git pull' failed in \"`pwd`\"."
        exit 1
    fi
fi
END
