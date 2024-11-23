package com.example.cowin_sms_grabber;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.telephony.SmsMessage;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.DataOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SMSListener extends BroadcastReceiver {

    private SharedPreferences preferences;

    @Override
    public void onReceive(Context context, Intent intent) {
        // TODO Auto-generated method stub

        final String URL = "https://r6kmoa2yi8.execute-api.us-east-1.amazonaws.com/cowin/post-otp";
        final String sender = android.os.Build.MODEL;

        if (intent.getAction().equals("android.provider.Telephony.SMS_RECEIVED")) {
            Bundle bundle = intent.getExtras();           //---get the SMS message passed in---
            SmsMessage[] msgs = null;
            if (bundle != null) {
                //---retrieve the SMS message received---
                try {
                    Object[] pdus = (Object[]) bundle.get("pdus");
                    msgs = new SmsMessage[pdus.length];
                    for (int i = 0; i < msgs.length; i++) {
                        msgs[i] = SmsMessage.createFromPdu((byte[]) pdus[i]);
                        final String msg_from = msgs[i].getOriginatingAddress();
                        String msgBody = msgs[i].getMessageBody();

                        if(msg_from.equalsIgnoreCase("AX-NHPSMS"))
                        {
                            if(msgBody.contains("OTP to register/access CoWIN is"))
                            {
                                Pattern pattern = Pattern.compile("CoWIN is(.*?)[.]");
                                final Matcher matcher = pattern.matcher(msgBody);
                                if(matcher.find()) {

                                    Thread thread = new Thread(new Runnable() {
                                        @Override
                                        public void run() {
                                            try
                                            {
                                                String otp = String.valueOf(matcher.group(1)).trim();




                                                java.net.URL url = new URL(URL);
                                                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                                                conn.setRequestMethod("POST");
                                                conn.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
                                                conn.setRequestProperty("Accept","application/json");
                                                conn.setDoOutput(true);
                                                conn.setDoInput(true);

                                                JSONObject jsonParam = new JSONObject();
                                                jsonParam.put("sender", msg_from);
                                                jsonParam.put("proxy", sender);
                                                jsonParam.put("otp", otp);

                                                DataOutputStream os = new DataOutputStream(conn.getOutputStream());
                                                os.writeBytes(jsonParam.toString());
                                                os.flush();
                                                os.close();

                                                conn.disconnect();
                                            }
                                            catch (Exception e)
                                            {
                                                e.printStackTrace();
                                            }
                                        }
                                    });

                                    thread.start();
                                }
                            }
                        }

                    }
                } catch (Exception e) {
                          Toast toast = Toast.makeText(context,"An error occurred " + e.getMessage(), Toast.LENGTH_LONG);
                          toast.show();
                }
            }
        }
    }
}