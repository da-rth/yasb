module.exports = {
  'env': {
    'browser': true,
    'es2021': true,
  },
  'extends': [
    'plugin:vue/vue3-essential',
    'google',
    'plugin:vue/base',
  ],
  'parser': 'vue-eslint-parser',
  'parserOptions': {
    'parser': '@typescript-eslint/parser',
    'sourceType': 'module',
    'ecmaVersion': 2018,
    'ecmaFeatures': {
      'globalReturn': false,
      'impliedStrict': false,
      'jsx': false,
    },
  },
  'plugins': [
    'vue',
    '@typescript-eslint',
  ],
  'rules': {
    'no-unused-vars': 'off',
    'vue/multi-word-component-names': 'off',
    'linebreak-style': ['error', 'windows'],
    'indent': ['error', 2],
    'max-len': ['error', {'code': 128}],
    'require-jsdoc': 'off',
  },
};
