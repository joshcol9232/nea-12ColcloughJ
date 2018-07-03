void onCreate(Bundle savedInstanceState){
  super.onCreate(savedInstanceState);
  mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
  if (mBluetoothAdapter == null){
    background(60);
    text("Device does not support bluetooth.", width/2, height/2);
  }
  else{
    boolean validBT = checkBT();
    if(!validBT){
      println("No paired devices.");
      if(mousePressed){
        System.exit(0);
      }
    }
  }
  if(!mBluetoothAdapter.isEnabled()){
    Intent turnOn = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
    startActivity(turnOn);
    //startActivityForResult(turnOn, REQ_BT_ENABLE);
    println("Enabling bluetooth.");
  }
  
  //IntentFilter filter = new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED);
}
