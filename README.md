docker build -t ipapi .
docker save ipapi -o ipapi.tar
```
||
||
||
\/
```
docker load -i /path/to/ipapi.tar

TODO:

сделать утилиту для обновления БД
