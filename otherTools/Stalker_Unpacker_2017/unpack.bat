for %%f in (..\*.db*) do (
    converter.exe -unpack -2947ru %%f -dir .\unpacked
)

pause