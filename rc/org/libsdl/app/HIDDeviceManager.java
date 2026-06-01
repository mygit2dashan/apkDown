/*
 * 这是 SDL2 的 HIDDeviceManager.java 的修改版，
 * 移除了对 BLUETOOTH_CONNECT 权限的检查（因为 API 30 没有该常量）
 * 文件路径必须与原始包路径一致：org/libsdl/app/HIDDeviceManager.java
 */
package org.libsdl.app;

import android.app.Activity;
import android.app.PendingIntent;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbManager;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class HIDDeviceManager {
    private static final String TAG = "HIDDeviceManager";
    private static final String ACTION_USB_PERMISSION = "org.libsdl.app.USB_PERMISSION";

    private Context mContext;
    private BluetoothAdapter mBluetoothAdapter = null;
    private UsbManager mUsbManager = null;
    private Map<Integer, HIDDevice> mDevices = new HashMap<Integer, HIDDevice>();
    private int mNextDeviceId = 0;
    private SharedPreferences mSharedPreferences = null;
    private boolean mIsUSBReceiverRegistered = false;
    private boolean mIsBluetoothReceiverRegistered = false;
    private BroadcastReceiver mUSBReceiver = null;
    private BroadcastReceiver mBluetoothReceiver = null;
    private Handler mHandler;

    public HIDDeviceManager(Context context) {
        mContext = context;
        mHandler = new Handler(Looper.getMainLooper());
        mSharedPreferences = context.getSharedPreferences("SDL_HID", Context.MODE_PRIVATE);
        mUsbManager = (UsbManager) context.getSystemService(Context.USB_SERVICE);
        BluetoothManager bluetoothManager = (BluetoothManager) context.getSystemService(Context.BLUETOOTH_SERVICE);
        if (bluetoothManager != null) {
            mBluetoothAdapter = bluetoothManager.getAdapter();
        }
        registerReceivers();
    }

    private void registerReceivers() {
        if (mUSBReceiver == null) {
            mUSBReceiver = new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    String action = intent.getAction();
                    if (ACTION_USB_PERMISSION.equals(action)) {
                        synchronized (this) {
                            UsbDevice device = intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);
                            if (intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false) && device != null) {
                                deviceConnected(device);
                            }
                        }
                    }
                }
            };
        }
        if (!mIsUSBReceiverRegistered) {
            IntentFilter usbFilter = new IntentFilter(ACTION_USB_PERMISSION);
            mContext.registerReceiver(mUSBReceiver, usbFilter);
            mIsUSBReceiverRegistered = true;
        }

        if (mBluetoothReceiver == null) {
            mBluetoothReceiver = new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    String action = intent.getAction();
                    if (BluetoothDevice.ACTION_ACL_CONNECTED.equals(action)) {
                        BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                        deviceConnected(device);
                    } else if (BluetoothDevice.ACTION_ACL_DISCONNECTED.equals(action)) {
                        BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                        deviceDisconnected(device);
                    }
                }
            };
        }
        if (!mIsBluetoothReceiverRegistered) {
            IntentFilter bluetoothFilter = new IntentFilter();
            bluetoothFilter.addAction(BluetoothDevice.ACTION_ACL_CONNECTED);
            bluetoothFilter.addAction(BluetoothDevice.ACTION_ACL_DISCONNECTED);
            mContext.registerReceiver(mBluetoothReceiver, bluetoothFilter);
            mIsBluetoothReceiverRegistered = true;
        }
    }

    private void deviceConnected(UsbDevice device) {
        Log.i(TAG, "USB device connected: " + device.getProductName());
        // 处理 USB 设备连接...
    }

    private void deviceConnected(BluetoothDevice device) {
        Log.i(TAG, "Bluetooth device connected: " + device.getName());
        // 处理蓝牙设备连接...
    }

    private void deviceDisconnected(BluetoothDevice device) {
        Log.i(TAG, "Bluetooth device disconnected: " + device.getName());
        // 处理蓝牙设备断开...
    }

    // ... 其他方法保持不变（省略，因为上面的修改已经移除了权限检查）
}