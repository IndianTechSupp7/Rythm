#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
uniform vec2 direction;  // (1, 0) horizontal, (0, 1) vertical
uniform float radius;    // blur size

void main() {
    vec3 sum = vec3(0.0);
    float total = 0.0;

    for (float i = -radius; i <= radius; i++) {
        float w = 1.0 - abs(i) / radius;
        sum += texture(imageTexture, fragmentTexCoord + direction * i / 500.0).rgb * w;
        total += w;
    }

    gl_FragColor = vec4(sum / total, 1.0);
}
