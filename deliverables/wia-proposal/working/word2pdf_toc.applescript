on run argv
  set inPath to item 1 of argv
  set outPath to item 2 of argv
  with timeout of 900 seconds
  tell application "Microsoft Word"
    set display alerts to none
    open POSIX file inPath
    set theDoc to active document
    try
      repeat with t in (tables of contents of theDoc)
        update t
      end repeat
    end try
    try
      repeat 2 times
        repeat with t in (tables of contents of theDoc)
          update page numbers t
        end repeat
      end repeat
    end try
    save as theDoc file name outPath file format format PDF
    close theDoc saving no
  end tell
  end timeout
end run
