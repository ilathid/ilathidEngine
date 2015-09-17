#include <Python.h>

/**
 * 8 + 8/4 + 8/4 = 12
 * Order is : (w*h) y bytes, (w*h)/4 * u, (w*h)/4 * v
 */
static PyObject *colorspace_yv2rgb(PyObject *self, PyObject *args)
{
    const unsigned char *ydata;
	const unsigned char *vdata, *udata;
    const int y_len1, v_len, u_len, szx, szy;
	int y_len;
	unsigned char *outdata;
	int out_i;
	int byte_i, byte_i2;
    
	int Y;
    int V;
    int U;
    int R,G,B;
	
	PyObject *ret;
	
    if (!PyArg_ParseTuple(args, "s#s#s#ii", &ydata, &y_len1, &udata, &u_len, &vdata, &v_len, &szx, &szy))
        return 0;

    y_len = y_len1;    
    if (y_len > szx*szy) y_len = szx*szy;
    
    if (y_len != u_len * 4) return 0;
    if (u_len != v_len) return 0;
    if (szx * szy != y_len) return 0;
    
    outdata = (unsigned char *)malloc(y_len*3);
    
    
    

    
    // Y
    byte_i = 0;
    for(byte_i = 0; byte_i < y_len; byte_i++){
        // out_i =   byte_i % szx + szx_p2 *(byte_i/ szx);
        byte_i2 = (byte_i % szx + szx    *(byte_i/(szx*2)))/2;
        
        Y = ydata[byte_i]  - 16;
        V = vdata[byte_i2] - 128;
        U = udata[byte_i2] - 128;
        //V = 128;
        //U = 128;
        
        // Red        
        #if true
        R =  1164*Y;
        G =  (R - 813 *V - 391*U)/1000;
        B =  (R + 2018*U)/1000;
        R =  (R + 1596*V)/1000;
        #else
        R =  12*Y;
        G =  (R - 8 *V - 4*U)/10;
        B =  (R + 20*U)/10;
        R =  (R + 16*V)/10;
        #endif
        
        if(R < 0)
            R = 0;
        else if(R > 255)
            R = 255;
        if(G < 0)
            G = 0;
        else if(G > 255)
            G = 255;
        if(B < 0)
            B = 0;
        else if(B > 255)
            B = 255;
        
        // The following is the most costly part!
        outdata[byte_i*3]   = R;
        outdata[byte_i*3+1] = G;
        outdata[byte_i*3+2] = B;
        
    }
    
    // return data2
    ret = Py_BuildValue("s#", outdata, y_len*3);
    free(outdata);
    return ret;
}

static PyMethodDef ColorspaceMethods[] = {
    {"yv2rgb",  colorspace_yv2rgb, METH_VARARGS,
     "Takes yv12 data string, and returns conversion to rgb."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initcolorspace(void)
{
    (void) Py_InitModule("colorspace", ColorspaceMethods);
}
