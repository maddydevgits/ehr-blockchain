from flask import Flask, render_template, redirect, request, session
from web3 import Web3, HTTPProvider
from time import sleep
from ca import *
import json

def connect_with_blockchain(acc):
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    if(acc==0):
        web3.eth.defaultAccount = web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=acc
    compiled_contract_path='../build/contracts/ehr.json'
    deployed_contract_address=ehrContractAddress

    with open(compiled_contract_path) as file:
        contract_json=json.load(file)
        contract_abi=contract_json['abi']

    contract=web3.eth.contract(address=deployed_contract_address,abi=contract_abi)
    return contract, web3

app=Flask(__name__)
app.secret_key='makeskilled'

@app.route('/')
def indexPage():
    return render_template('index.html')

@app.route('/register')
def registerPage():
    return render_template('register.html')

@app.route('/registerUser',methods=['GET','POST'])
def registerUser():
    username=request.form['username']
    walletaddr=request.form['walletaddr']
    password=int(request.form['password'])
    role=request.form['role']
    print(username,walletaddr,password,role)
    if(role=='Doctor'):
        print('Registering as Doctor')
        contract,web3=connect_with_blockchain(0)
        tx_hash=contract.functions.addDoctor(walletaddr,username,password).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
    elif(role=='Patient'):
        print('Registering as Patient')
        contract,web3=connect_with_blockchain(0)
        tx_hash=contract.functions.addPatient(walletaddr,username,password).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
    return render_template('login.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/loginUser',methods=['GET','POST'])
def loginUser():
    walletaddr=request.form['walletaddr']
    password=int(request.form['password'])
    role=''
    contract,web3=connect_with_blockchain(0)
    _doctors,_dnames,_dpasswords=contract.functions.viewDoctors().call()
    _patients,_pnames,_ppasswords=contract.functions.viewPatients().call()

    if walletaddr in _doctors:
        role='Doctor'
    elif walletaddr in _patients:
        role='Patient'
    print(role)
    if role=='Doctor':
        doctorIndex=_doctors.index(walletaddr)
        if(_dpasswords[doctorIndex]==password):
            session['walletaddr']=walletaddr
            return redirect('/ddashboard')
        else:
            return redirect('/login')
    
    if role=='Patient':
        patientIndex=_patients.index(walletaddr)
        if(_ppasswords[patientIndex]==password):
            session['walletaddr']=walletaddr
            return redirect('/pdashboard')
        else:
            return redirect('/login')

@app.route('/ddashboard')
def ddashboard():
    data=[]
    walletaddr=session['walletaddr']
    contract,web3=connect_with_blockchain(0)
    _cdoctors,_cpatients,_cdates,_cstatus,_cmessages=contract.functions.viewAppointments().call()
    for i in range(len(_cdoctors)):
        if _cdoctors[i]==walletaddr:
            if _cstatus[i]==False:
                dummy=[]
                dummy.append(_cpatients[i])
                dummy.append(_cdates[i])
                data.append(dummy)
    l=len(data)
    return render_template('ddashboard.html',dashboard_data=data,len=l)

@app.route('/pdashboard')
def pdashboard():
    data=[]
    contract,web3=connect_with_blockchain(0)
    _doctors,_dnames,_dpasswords=contract.functions.viewDoctors().call()
    for i in range(len(_doctors)):
        dummy=[]
        dummy.append(_doctors[i])
        dummy.append(_dnames[i])
        data.append(dummy)
    l=len(data)
    return render_template('pdashboard.html',dashboard_data=data,len=l)

@app.route('/bookappointmentform',methods=['GET','POST'])
def bookappointmentform():
    walletaddr=session['walletaddr']
    doctorform=request.form['doctorform']
    date=request.form['date']
    print(doctorform,date)
    contract,web3=connect_with_blockchain(0)
    tx_hash=contract.functions.createAppointment(doctorform,walletaddr,str(date)).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/pdoctorcons')

@app.route('/pdoctorcons')
def pdoctorcons():
    data=[]
    walletaddr=session['walletaddr']
    contract,web3=connect_with_blockchain(0)
    _cdoctors,_cpatients,_cdates,_cstatus,_cmessages=contract.functions.viewAppointments().call()
    for i in range(len(_cdoctors)):
        if _cpatients[i]==walletaddr:
            dummy=[]
            dummy.append(_cdoctors[i])
            dummy.append(_cdates[i])
            dummy.append(_cstatus[i])
            dummy.append(_cmessages[i])
            data.append(dummy)
    
    l=len(data)
    return render_template('pdoctorcons.html',dashboard_data=data,len=l)


@app.route('/logout')
def logoutPage():
    return render_template('index.html')

@app.route('/book/<id>')
def consultPatient(id):
    print(id)
    session['pid']=id
    return redirect('/consultPatient')

@app.route('/consultPatient')
def consultpatient():
    return render_template('consultpatient.html')

@app.route('/consultpatientform',methods=['GET','POST'])
def consultpatientform():
    message=request.form['message']
    doctor=session['walletaddr']
    patient=session['pid']
    contract,web3=connect_with_blockchain(0)
    tx_hash=contract.functions.treatPatient(doctor,patient,message).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/dmypatients')

@app.route('/dmypatients')
def dmypatients():
    data=[]
    doctor=session['walletaddr']
    contract,web3=connect_with_blockchain(0)
    _cdoctors,_cpatients,_cdates,_cstatus,_cmessages=contract.functions.viewAppointments().call()
    for i in range(len(_cdoctors)):
        if _cdoctors[i]==doctor:
            dummy=[]
            dummy.append(_cpatients[i])
            dummy.append(_cdates[i])
            dummy.append(_cstatus[i])
            dummy.append(_cmessages[i])
            data.append(dummy)
    l=len(data)
    return render_template('dmypatients.html',dashboard_data=data,len=l)

if __name__=="__main__":
    app.run(debug=True)