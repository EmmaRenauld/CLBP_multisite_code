for file in logs/*
do
	s=`grep -o -m 1 'sub-[^ ]*' $file`
	s=${s%%...}
	echo $s
	mv $file logs/$s.log
done
