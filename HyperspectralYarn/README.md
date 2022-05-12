# Hyperspectral execution on yarn cluster
This project creates, startup and provisions 3 virtual machines which will be used as workers on a yarn cluster. Only the workers will be created, so is assumed that you have a yarn cluster well configured on the master node machine. Follow steps assumes that will be executed from the yarn master node machine.

Step 1: Start up, provision and configure the 3 workers:
```bash
	vagrant up
```

Step 2: Add virtual private network ips to your hosts file
```bash
	sudo echo 192.168.56.1    hadoop-master >> /etc/hosts
	sudo echo 192.168.56.2    hadoop-worker1 >> /etc/hosts
	sudo echo 192.168.56.3    hadoop-worker2 >> /etc/hosts
	sudo echo 192.168.56.4    hadoop-worker3 >> /etc/hosts
```

Step 3: Generate a public key to connect via ssh with all nodes (include master one).
Use 'vagrant' as password for virtual machines.
```bash
	ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa_master
	ssh-copy-id hadoop-master

	ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa_worker1
	ssh-copy-id vagrant@hadoop-worker1

	ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa_worker2
	ssh-copy-id vagrant@hadoop-worker2

	ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa_worker3
	ssh-copy-id vagrant@hadoop-worker3
```
Step 4: Add workers to yarn cluster configuration
```bash
	cp hadoop/workers /opt/hadoop/etc/hadoop/workers
```

Step 5: Set yarn.nodemanager.resource.cpu-vcores yarn cluster property to 4. 
You can do that copying ./hadoop/yarn-site.xml to your hadoop folder:
```bash
	cp hadoop/yarn-site.xml /opt/hadoop/etc/hadoop/yarn-site.xml
```

Step 6: Start up yarn cluster
```bash
	hdfs namenode -format
	/opt/hadoop/sbin/start-dfs.sh
	/opt/hadoop/sbin/start-yarn.sh
```

Step 7: Copy b0.txt file to hadoop file system
```bash
	hdfs dfs -copyFromLocal hyperspectral/b0.txt /user/hadoop/b0.txt
```

Step 8: Create spark log folder on hadoop file system
```bash
	hdfs dfs -mkdir -p /user/hadoop/spark-logs
```

Step 9: Execute hyperspectral spark algorithm
```bash
	spark-submit --master yarn --deploy-mode cluster hyperspectral/hyperspectral.py -i hdfs://hadoop-master:9000/user/hadoop/b0.txt
```

Step 10: Copy output result from hadoop file system
```bash
	hdfs dfs -copyToLocal /user/hadoop/out .
```