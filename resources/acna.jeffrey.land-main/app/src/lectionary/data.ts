import raw from '../data/dailyOfficeLectionary.json'

export interface LessonPair {
  lesson1: string
  lesson2: string
}

export interface DateEntry {
  yearI?: LessonPair
  yearII?: LessonPair
}

export interface MovableEntry {
  morningPsalm: string
  morningLesson1: string
  morningLesson2: string
  eveningPsalm: string
  eveningLesson1: string
  eveningLesson2: string
}

export interface LectionaryData {
  psalms30Day: Record<string, { morning: string; evening: string }>
  byDate: Record<string, DateEntry>
  movable: {
    ashWednesday: MovableEntry
    maundyThursday: MovableEntry
    goodFriday: MovableEntry
    holySaturday: MovableEntry
    easterDay: MovableEntry
    ascensionDay: MovableEntry
    pentecost: MovableEntry
  }
}

export const lectionary = raw as unknown as LectionaryData
