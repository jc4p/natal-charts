import { h, Component } from 'preact';
import moment from 'moment';

const MonthPicker = ({ onChange, ...props }) => (
  <select onChange={onChange} id="select-month">{ optionsFor("month", props.date) }</select>
);

const DayPicker = ({ onChange, ...props }) => (
  <select onChange={onChange} id="select-date">{ optionsFor("day", props.date) }</select>
);

const YearPicker = ({ onChange, ...props }) => (
  <select onChange={onChange} id="select-year">{ optionsFor("year", props.date) }</select>
);

const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']  
const startYear = 1930;
const endYear = 2018;

function optionsFor(field, selectedDate) {
  if (field === 'year') {
    selected = selectedDate.year();

    return [...Array(endYear-startYear).keys()].map((item, i) => {
      var isSelected = (startYear + item) == selected;
      return (
        <option value={startYear + item} selected={isSelected ? 'selected' : ''}>{startYear + item}</option>
      );
    });
  }
  else if (field === 'month') {
    selected = selectedDate.month();
    return months.map((item, i) => {
      var isSelected = i == selected;
      return (
        <option value={i} selected={isSelected ? 'selected' : ''}>{item}</option>
      );
    });
  }
  else if (field === 'day') {
    var selected = selectedDate.date();
    var firstDay = 1;
    var lastDay = moment(selectedDate).add(1, 'months').date(1).subtract(1, 'days').date() + 1;
    return [...Array(lastDay-firstDay).keys()].map((item, i) => {
      var isSelected = (item + 1) == selected;
      return (
        <option value={item + 1} selected={isSelected ? 'selected': ''}>{item + 1}</option>
      )
    });
  }
}

export default class DatePicker extends Component {
  constructor(props) {
    super(props);

    this.state = {
      date: props.date
    };

    this.onChange = this.onChange.bind(this);
  }

  onChange(event) {
    var month = document.getElementById('select-month').value;
    var day = document.getElementById('select-date').value;
    var year = document.getElementById('select-year').value;

    var newDate = moment().year(year).month(month).date(day);
    this.setState({ date: newDate })
    this.props.onChange(newDate);
  }

  render() {
    return (
      <div>
        <MonthPicker date={this.state.date} onChange={this.onChange} />
        <DayPicker date={this.state.date} onChange={this.onChange} />
        <YearPicker date={this.state.date} onChange={this.onChange} />
      </div>
    )
  }
}