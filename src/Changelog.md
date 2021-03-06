#Changelog
* v0.1.1 - First alpha release
* v0.1.2 - Minor alpha release
	* added support for Spark monitoring
	* modified logstash conf generation to include graphite input 
* v0.1.3 - Minor alpha release
	* added jmxtrans install to pysshCore
	* added the capability to define node roles
	* added the capability to start/stop all auxiliary components
	* added the capability to start/stop auxiliary components on specified nodes
	* updated kibana version from 4.0.2 to 4.1.2
	* enabled import export of kibana dashboard
	* added resources to controll kibana instance
	* created pid file directory for core components
	* created log file directory for core components
	* created dmon-stop script
	* enhanced queryConstructor function to enable elasticsearch date math
	* updated all Vagrant files
* v0.1.4 - Minor alpha release
	* added log export resource
	* added parallel processing of some requests (marked with _../v2/.._)
	* added new dmon-agent for controlling auxiliary monitoring components
	* added dmon-wui template to respoitory
* v0.2.0 - Major alpha release
	* updated minimum requirements
		* Elasticsearch 2.*
		* Logstash 2.*
		* Kibana 4.4.*
		* updated start scripts for default metrics (env. variables)
		* added aditional metrics to ls and es configurations
		* added automatic storm topology detection
		* added polling period definition
		* added dmon-agent bootstrapping resources
		* split app from main reource file
		* added OSLC Perf Mon v2 for system metrics
		* created additional resources
			* dmon-logstash
			* dmon-elastisearch
		* added branding to kibana dashboard
		* added logging system to all services
		* updated stop scripts with pid file removal
		* added root user check in start scripts
		* added support for Storm monitoring
		* major overhaul of logstash template
* v0.2.3 - Minor alpha release
	* added support for Cassandra
	* added support for MongoDB
	* various bug and performance issues fixed   
* v0.2.4 - Minor alpha release
	* updated vagrant scripts
	* added Chef based bootstrap resources
	* added support for advanced MongoDB query aggregations
	* added support for advanced Cassandra query aggregations 	
	* implemented graceful shutdown of supporting services
	* finalized default Storm visualisations
	* added new timeout definition mechanism (env variable _DMON\_TIMEOUT_)
	* added D-Mon artifact repository for ADT model saving and retrieval	 	
