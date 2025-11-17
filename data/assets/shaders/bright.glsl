#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

void main() {
    vec3 col = texture(imageTexture, fragmentTexCoord).rgb;

    float brightness = dot(col, vec3(0.2126, 0.7152, 0.0722)); // luminance

    if (brightness > 0.7)   // threshold
        gl_FragColor = vec4(col, 1.0);
    else
        gl_FragColor = vec4(0.0);
}
