// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;
pragma experimental ABIEncoderV2;

contract ehr {
  
  address[] _doctors;
  string[] _dnames;
  uint[] _dpasswords;

  address[] _patients;
  string[] _pnames;
  uint[] _ppasswords;

  address[] _cpatients;
  address[] _cdoctors;
  string[] _cmessages;
  string[] _cdates;
  bool[] _cstatus;

  function addDoctor(address doctor, string memory name, uint password) public {
    _doctors.push(doctor);
    _dnames.push(name);
    _dpasswords.push(password);
  }

  function viewDoctors() public view returns(address[] memory, string[] memory, uint[] memory) {
    return(_doctors,_dnames,_dpasswords);
  }

  function addPatient(address patient, string memory name, uint password) public {
    _patients.push(patient);
    _pnames.push(name);
    _ppasswords.push(password);
  }

  function viewPatients() public view returns(address[] memory, string[] memory, uint[] memory){
    return(_patients,_pnames,_ppasswords);
  }

  function createAppointment(address doctor, address patient, string memory date) public {
    _cdoctors.push(doctor);
    _cpatients.push(patient);
    _cdates.push(date);
    _cstatus.push(false);
    _cmessages.push("");
  }

  function treatPatient(address doctor, address patient, string memory cons) public{

    uint i;
    for(i=0;i<_cdoctors.length;i++) {
      if(_cdoctors[i]==doctor && _cpatients[i]==patient) {
        _cstatus[i]=true;
        _cmessages[i]=cons;
      }
    }
  }

  function viewAppointments() public view returns(address[] memory, address[] memory,string[] memory,bool[] memory,string[] memory) {
    return (_cdoctors,_cpatients,_cdates,_cstatus,_cmessages);
  }

}
