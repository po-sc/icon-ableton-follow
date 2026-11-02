// color_test: 20 секунд показывает на контроллере 8 цветов и надписи P1 CH 1..8, затем всё гасит.
// Отвечает на вопрос, умеет ли экран показывать цвета дорожек. Шлёт во все порты iCON:
// цифра после P в надписи покажет, какой порт слушает активный слот контроллера.
// Перед запуском закрыть Ableton.
// Запуск: swift tools/color_test.swift            (все порты iCON)
//         swift tools/color_test.swift "Порт 1"   (только этот порт)
//         swift tools/color_test.swift --list     (только показать порты)
import CoreMIDI
import Foundation

func name(_ e: MIDIEndpointRef) -> String {
    var s: Unmanaged<CFString>?
    MIDIObjectGetStringProperty(e, kMIDIPropertyDisplayName, &s)
    return s?.takeRetainedValue() as String? ?? "?"
}

let argument = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : ""
let destinations = (0..<MIDIGetNumberOfDestinations()).map { MIDIGetDestination($0) }

if argument == "--list" {
    destinations.forEach { print(name($0)) }
    exit(0)
}
let targets = destinations.filter { (name($0).contains("P1") || name($0).contains("iCON")) && (argument.isEmpty || name($0).contains(argument)) }
guard !targets.isEmpty else {
    print("Порт iCON \(argument) не найден. Есть:")
    destinations.forEach { print("  " + name($0)) }
    exit(1)
}

var client = MIDIClientRef()
MIDIClientCreateWithBlock("color_test" as CFString, &client) { _ in }
var port = MIDIPortRef()
MIDIOutputPortCreate(client, "out" as CFString, &port)

func send(_ bytes: [UInt8], to target: MIDIEndpointRef) {
    var list = MIDIPacketList()
    let packet = MIDIPacketListInit(&list)
    _ = MIDIPacketListAdd(&list, MemoryLayout<MIDIPacketList>.size, packet, 0, bytes.count, bytes)
    MIDISend(port, target, &list)
}

let colorHeader: [UInt8] = [0xF0, 0x00, 0x02, 0x4E, 0x16, 0x14]
let namesHeader: [UInt8] = [0xF0, 0x00, 0x00, 0x66, 0x14, 0x12, 0x00]
let colors: [[UInt8]] = [
    [127, 0, 0], [127, 60, 0], [127, 127, 0], [0, 127, 0],
    [0, 127, 127], [0, 0, 127], [80, 0, 127], [127, 127, 127],
]

// Номер порта для надписи: последняя цифра в имени, "iCON P1-Nano Порт 2" -> 2
func portNumber(_ target: MIDIEndpointRef) -> String {
    name(target).last(where: { $0.isNumber }).map(String.init) ?? "?"
}

func show(_ target: MIDIEndpointRef, names: String, rgb: [[UInt8]]) {
    send(colorHeader + rgb.flatMap { $0 } + [0xF7], to: target)
    send(namesHeader + Array(names.padding(toLength: 56, withPad: " ", startingAt: 0).utf8) + [0xF7], to: target)
}

print("Отправляю в: \(targets.map(name).joined(separator: ", ")). Смотри на экран контроллера 20 секунд.")
for _ in 0..<80 {
    for target in targets {
        show(target, names: (1...8).map { "P\(portNumber(target)) CH \($0)" }.joined(), rgb: colors)
    }
    Thread.sleep(forTimeInterval: 0.25)
}
for target in targets {
    show(target, names: "", rgb: Array(repeating: [0, 0, 0], count: 8))
}
print("Готово, экран очищен.")
print("Надписи и цвета: экран показывает цвета.")
print("Только надписи: связь есть, но цветов нет. Возможно, так устроен этот экран или нужна другая прошивка.")
print("Ничего: контроллер не в DAW-режиме или экран не принимает эти команды.")
