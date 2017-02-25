import { h, render, Component } from 'preact';

let SetupView = require('./src/setup').default;

const renderApp = (Component) => {
  let rootView = document.getElementById('root');
  render(<Component />, rootView, rootView.lastChild);
};

if (module.hot) {
  module.hot.accept('./src/setup', () => {
    let SetupView = require('./src/setup').default;
    renderApp(SetupView);
  });
}


renderApp(SetupView);