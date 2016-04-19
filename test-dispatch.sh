./test-dispatch 172.16.60.10
for i in `seq 59`; do  ./test-dispatch 172.16.1.$i & done
netstat -nalp | grep 8773
for i in `seq 59`; do ssh 172.16.1.$i netstat -nalp | grep 8773; done
