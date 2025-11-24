#version 330 core

in vec3 fragmentColor;
in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;
uniform sampler2D stars;
uniform sampler2D noiseTex;
uniform float time;
uniform vec3 bg = vec3(0.55, 0.71, 1.0);
uniform vec3 color1 = vec3(0.36, 0.65, 0.46);
uniform vec3 color2 = vec3(0.41, 0.78, 0.42);
uniform vec3 color3 = vec3(0.67, 0.8666, 0.39);
uniform vec3 layers = vec3(0.2, 0.35, 0.4);
uniform int uRadius = 5;
uniform vec2 uTexSize;

void main() {
  vec2 uv = fragmentTexCoord.xy;
  vec2 texel = 1.0 / uTexSize;
  float t = time * 0.2;

  vec4 result = vec4(0.0);
  float total = 0.0;
  vec4 star = texture2D(stars, uv);
  // float rnd = max(texture2D(noiseTex, uv + t).x * 0.6, 0.2);
  // star *= rnd;

  for(float i = -uRadius; i <= uRadius; i++) {
    float weight = exp(-0.5 * (i * i) / (uRadius * uRadius));

    vec2 offsetX = vec2(i * texel.x, 0.0);
    vec2 offsetY = vec2(0.0, i * texel.y);

    vec4 sX = texture(stars, uv + offsetX);
    vec4 sY = texture(stars, uv + offsetY);

    result += sX * weight * max(0.0, sX.r * 2.0 - 1.0);   // horizontal
    result += sY * weight * max(0.0, sY.r * 2.0 - 1.0);   // vertical

    total += weight * weight;
  }

  star += result / (total);
  //star *= max(texture2D(noiseTex, uv + t).x * 0.6, 0.2);
  //vec3 color = mix(vec3(bg), star.rgb, star.rgb);
  vec3 color = bg + star.rgb;
  float s1 = sin(uv.x + t * 1.9) * 0.07;
  float s2 = sin(uv.x + t * 1.2 + 0.6) * 0.05;
  float s3 = sin(uv.x + t * 0.9 - 1.93) * 0.09;

  //float s1 = sin(time*2+uv.x)*0.1;
  // float s2 = sin(time*0.1 + uv.x);
  // float s3 = sin(time*0.1 + uv.x);

  color = mix(color, color3, 1. - step(0., uv.y - layers.z + s3));
  color = mix(color, color2, 1. - step(0., uv.y - layers.y + s2));
  color = mix(color, color1, 1. - step(0., uv.y - layers.x + s1));

  vec4 surf = texture2D(imageTexture, uv);
  gl_FragColor = vec4(mix(color, surf.rgb, vec3(surf.a)).rgb, 1.0);
}