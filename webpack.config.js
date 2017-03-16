var webpack = require('webpack');
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
      { test: /\.css$/, use: [ { loader: 'style-loader'}, { 'loader': 'css-loader' } ] },
      { test: /\.scss$/, use: [ 'style-loader', 'css-loader', 'sass-loader' ] }
    ]
  },
  resolve: {
    alias: {
      'react': 'preact-compat',
      'react-dom': 'preact-compat'
    }
  },
  plugins: [
    new webpack.optimize.UglifyJsPlugin({
      compress: {
        warnings: false,
        drop_console: false
      }
    }),
  ],
  devtool: 'cheap-module-eval-source-map',
  devServer: {
    port: 3000
  }
};
