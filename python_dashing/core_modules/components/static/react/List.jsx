import React, {Component, PropTypes} from 'react';
import css from './List.css';
import WidgetBox from './WidgetBox.jsx';

export default class List extends Component {
  render() {
    let {showNumbers, data, title} = this.props;
    if (!data) {data = [];}
    const list = data.map((item) => {
      return (<li>{item}</li>);
    });
    const styles = {
      'list-style-type': showNumbers ? "decimal" : "none"
    };
    return (
      <WidgetBox className={css.container}>
        <h1 className={css.heading}>{this.props.title}</h1>
        <ol className={css.list} styles={styles}>
          {list}
        </ol>
      </WidgetBox>
    );
  }
}

Number.propTypes = {
  data: PropTypes.arrayOf(PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ])),
  showNumbers: PropTypes.bool,
  title: PropTypes.string,
};
