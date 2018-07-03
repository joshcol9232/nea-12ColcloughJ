class BluetoothConnectionService{
  private static final String appName = "MYAPP";
  private final UUID MY_UUID = UUID.fromString("d4ba26a4-f821-46ed-a3ad-5e3d2ac2e710");
  private final BluetoothAdapter mBluetoothAdapter;
  Context mContext;
  
  public BluetoothConnectionService(Context context){
    mContext = context;
    mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
  }
  
  private class AcceptThread extends Thread{
    private final BluetoothServerSocket mmServerSocket;
    
    public AcceptThread(){
      BluetoothServerSocket tmp = null;
      try{
        tmp = mBluetoothAdapter.listenUsingInsecureRfcommWithServiceRecord(appName, MY_UUID);
        println("Setting up accept thread.");
      }catch (IOException e){
        println("Error setting up accept thread." + e.getMessage());
      }
      mmServerSocket = tmp;
    }
    public void run(){
      println("Accept thread running.");
      BluetoothSocket socket = null;
      try{
        println("Server socket waiting.");
        socket = mmServerSocket.accept();
        println("Server socket accepted a connection.");
      }catch(IOException e){
        println("Accept thread had IOException " + e.getMessage());
      }
      if (socket != null){
        connected(socket, mmDevice);
      }
    }
    public void cancel(){
      println("Cancelling accept thread.");
      try{
        mmServerSocket.close();
      }catch (IOException e){
        println("Closing accept thread socket failed." + e.getMessage());
      }
    }
  }
}
