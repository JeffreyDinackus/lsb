const INTENTIONS = [
  'For the joy of the resurrection among us; for the fruit of faith nourished by the Word and the Sacraments.',
  'For faith to live in the promises of Holy Baptism; for one’s calling and daily work; for the unemployed; for the salvation and well-being of our neighbors; for schools, colleges, and seminaries; for good government and for peace.',
  'For deliverance against temptation and evil; for the addicted and despairing, the tortured and oppressed; for those struggling with sin.',
  'For marriage and family, that husbands and wives, parents and children live in ordered harmony according to the Word of God; for parents who must raise children alone; for our communities and neighborhoods.',
  'For the Church and her pastors; for teachers, deaconesses, and other church workers; for missionaries and for all who serve the Church; for fruitful and salutary use of the blessed Sacrament of Christ’s body and blood.',
  'For the preaching of the holy cross of our Lord Jesus Christ and for the spread of His knowledge throughout the whole world; for the persecuted and oppressed; for the sick and dying.',
  'For faithfulness to the end; for the renewal of those who are withering in the faith or have fallen away; for receptive hearts and minds to God’s Word on the Lord’s Day; for pastors and people as they prepare to administer and receive Christ’s holy gifts.',
]

const WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

/** The suggested intercessions for today's weekday, from the Daily Prayer introduction. */
export function WeekdayIntention() {
  const dow = new Date().getDay()
  return (
    <p className="b-weekday">
      <span className="b-weekday-label">{WEEKDAYS[dow]}</span>
      <span className="b-weekday-text">{INTENTIONS[dow]}</span>
    </p>
  )
}
