#include "ma.h"


void MA_SendData(int16_t *data, int8_t datalen){
    MA_Send_Bytes_CallBack(Frame_B_1);
    MA_Send_Bytes_CallBack(Frame_B_2);
    for(int i=0;i<datalen;i++){
        
        MA_Send_Bytes_CallBack(data[i]);
        MA_Send_Bytes_CallBack(data[i]>>8);
    }
    MA_Send_Bytes_CallBack(Frame_E_1);
    MA_Send_Bytes_CallBack(Frame_E_2);
}


void MA_Send_Bytes_CallBack(uint_8_t data){

    //回调函数,更换为自己的串口发送函数

}