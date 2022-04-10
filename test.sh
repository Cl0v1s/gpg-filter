for file in test/*
do
    cat "$file" | python3 main.py clovis@bdx.town > "$file.pgp.eml"
done
