#!flask/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, jsonify, abort
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import *

# App config
DEBUG = True
app = Flask(__name__,static_url_path='/templates')
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


@app.route("/<address>:<port>", methods=['GET'])
def index(address,port):
	client = ModbusTcpClient(str(address),int(port))
	succeed = client.connect()

	if not succeed:
		client.close()
		abort(404, description="Connection to modbus slave failed! Check IP address and port on the URL.")
	else:
		return render_template('index.html', address=address, port=port)


@app.route("/<address>:<port>/get_values")
def get_values(address,port):

	client = ModbusTcpClient(str(address), int(port))
	succeed = client.connect()

	if succeed:
		result = client.read_holding_registers(address=0,count=15,unit=1)
		result2 = client.read_coils(address=0,count=15,unit=1)
		client.close()
		results = {}
		for r in range(0,15):
			register = result.registers[r]
			results["r"+str(r)] = str(register)+"%"
			
			coil = result2.bits[r]
			if coil:
				coil='ON'
			else:
				coil='OFF'

			results["c"+str(r)] = coil

		#print(results)

		return jsonify(results)
	else:
		return render_template('index.html', error="Modbus slave is disconnected")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
