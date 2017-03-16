import { h, Component } from 'preact';
import moment from 'moment';

import DatePicker from './components/DatePicker.js';

import styles from './styles.scss';

export default class SetupView extends Component {
  constructor(props) {
    super(props);

    this.state = {
      birthdate: moment()
    }

    this.onNameChange = this.onNameChange.bind(this);
    this.onBirthdateChange = this.onBirthdateChange.bind(this);
    this.onBirthCityChange = this.onBirthCityChange.bind(this);
  }

  onNameChange(event) {
    this.setState({name: event.target.value});
  }

  onBirthdateChange(newDate) {
    this.setState({birthdate: newDate});
  }

  onBirthCityChange(event) {
    this.setState({birth_city: event.target.value});
  }

  render() {
    return (
      <div styles={styles.mainContainer}>
        <h1>You & and Your Birth</h1>
        <form>
          <div>
            <label>
            Name:
            <input type="text" value={this.state.name} onChange={this.onNameChange} />
            </label>
          </div>
          <div>
            <label>
            Birthday:
            <DatePicker date={this.state.birthdate} onChange={this.onBirthdateChange} />
            </label>
          </div>
          <div>
            <label>
            Birth city:
            <input type="text" value={this.state.birth_city} onChange={this.onBirthCityChange} />
            </label>
          </div>
        </form>
      </div>
    )
  }
}
