#version 330 core

in vec3 fragmentColor;
in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;
uniform sampler2D noiseTexture;
uniform sampler2D bgTexture;
uniform float time;
uniform float radius = 7;
uniform vec3 vg_color = vec3(1.0, 0.0, 0.0);

void main() {
    vec2 uv = fragmentTexCoord.xy;
    vec2 noise = texture(noiseTexture, uv + time * 0.1).xy;
    vec3 bg = texture(bgTexture, (uv + noise * 0.02)).rgb;
    float blue_blend = min(time, 2.0) / 2.0;

    vec3 colorSum = vec3(0.0);
    float totalWeight = 0.0;

    // --- Blur RGB ---
    for(float x = -radius; x <= radius; x++) {
        for(float y = -radius; y <= radius; y++) {
            // weight (simple falloff)
            float dist = length(vec2(x, y));
            float weight = max(radius - dist, 0.0);

            vec4 col = texture(imageTexture, uv + vec2(x, y) / 1000.0).rgba;

            colorSum += col.rgb * weight * 0.6 * col.a;
            totalWeight += weight;
        }
    }

    vec3 blurredRGB = colorSum / totalWeight;
    vec4 tex = texture(imageTexture, uv);
    //vec3 n_bg = bg + vec3(0.0, 0.0, 1.0) * blue_blend * 0.1 * length(uv - vec2(.5, 0.)) * 0.8;

    gl_FragColor = vec4((blurredRGB + bg) * (1.0 - tex.a) + tex.rgb * tex.a + vg_color * .5 * length(uv - vec2(.5, 0.)) * 0.8, 1.0);

    //gl_FragColor = vec4(blurredRGB + tex.rgb + bg, 1.0);
    //gl_FragColor = vec4(pow(uv.y, 4), 0., 0., 0.);
}//texture2D(imageTexture, (uv + noise)).xyz