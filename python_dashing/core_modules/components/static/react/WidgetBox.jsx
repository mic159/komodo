import React, {Component, PropTypes} from 'react';
import styles from '/modules/python_dashing.server/Dashboard.css';

export default class WidgetBox extends Component {
  constructor(props) {
    super(props);
    this.state = {data: this.props.data};
  }

  render() {
    const style = {
      backgroundColor: this.props.color,
    };
    let className = styles.widget;
    if (this.props.className) {
      className += ' ' + this.props.className;
    }
    return <div className={className} style={style}>{this.render_inner().props.children}</div>;
  }

  loadData() {
    fetch(this.props.datasource)
      .then(data => data.json())
      .then(data => {
        this.setState({data: data});
      })
  }

  componentDidMount() {
    // Poll every "every" seconds for data
    setInterval(this.loadData.bind(this), this.props.every || 30000);
    this.loadData();
  }
}

WidgetBox.propTypes = {
  every: PropTypes.number,
  children: PropTypes.array,
  color: PropTypes.string,
  className: PropTypes.string,
  datasource: PropTypes.string.isRequired
};
