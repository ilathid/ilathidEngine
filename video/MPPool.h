void init_shaders();

int MPP_create(const char *filename, int looping, const char *audio_class);
void MPP_play(int mp);
void MPP_stop(int mp);
void MPP_close(int mp);
int MPP_getWidth(int mp);
int MPP_getHeight(int mp);
