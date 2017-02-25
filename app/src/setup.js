import { h, Component } from 'preact';
import Select from 'react-select';
import moment from 'moment';

require('react-select/dist/react-select.css');

export default class SetupView extends Component {
  constructor(props) {
    super(props);

    this.onNameChange = this.onNameChange.bind(this);
    
    this.birthOptionDays = [];
    this.birthOptionsMonths = [];
    this.birthOptionYears = [];

    let months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']  
    months.map((item, i) => {
      this.birthOptionsMonths.push({value: i + 1, label: item});
    });

    [...Array(30).keys()].map((item, i) => {
      this.birthOptionDays.push({value: item + 1, label: item + 1});
    });

    [...Array(2017-1900).keys()].map((item, i) => {
      this.birthOptionYears.push({value: 1900 + item, label: 1900 + item});
    });
  }

  onNameChange(event) {
    this.setState({name: event.target.value});
  }

  render() {
    return (
      <div>
        <h1>You & Your Birth</h1>
        <form>
          <label>
          Name:
          <input type="text" value={this.state.name} onChange={this.onNameChange} />
          </label>
          <label>
          Birthday:
          <Select value="January" options={this.birthOptionsMonths} onChange={this.onBirthMonthChange} />
          <Select value={1} options={this.birthOptionDays} onChange={this.onBirthDayChange} />
          <Select value={1980} options={this.birthOptionYears} onChange={this.onBirthYearChange} />
          </label>
        </form>
      </div>
    )
  }
}
