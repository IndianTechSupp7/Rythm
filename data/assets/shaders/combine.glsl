#version 330 core

in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;     // original screen
uniform sampler2D bloomTexture;     // blurred bright pass

void main() {
    vec3 original = texture(imageTexture, fragmentTexCoord).rgb;
    vec3 bloom = texture(bloomTexture, fragmentTexCoord).rgb;

    gl_FragColor = vec4(original + bloom * 1.5, 1.0);  // bloom intensity
}
