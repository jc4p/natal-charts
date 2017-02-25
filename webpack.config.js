var path = require('path');

module.exports = {
  entry: './app/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  module: {
    rules: [
      { test: /\.js$/, exclude: /node_modules/, use: [ { loader: "babel-loader" } ] },
      { test: /\.css$/, use: [ { loader: 'style-loader'}, { 'loader': 'css-loader' } ] }
    ]
  },
  resolve: {
    alias: {
      'react': 'preact-compat',
      'react-dom': 'preact-compat'
    }
  },
  devServer: {
    port: 3000
  }
};
