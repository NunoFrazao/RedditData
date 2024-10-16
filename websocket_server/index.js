const httpServer = require('http').createServer()

const PORT = 8082
const io = require("socket.io")(httpServer, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"],
        credentials: true
    }
})

httpServer.listen(PORT, () => {
    console.log('listening on *:' + PORT)
})

io.on('connection', (socket) => {
    console.log(`client ${socket.id} has connected`)

    socket.on('loggedIn', function (user) {
        socket.join(user.email)
        if (user.tipo_user == '1') {
            socket.join('administrator')
        } else {
            socket.join(user)
        }
    })

    socket.on('newUser', (user) => {
        socket.in('administrator').emit('newUser', user)
    })

    socket.on('userChange', (user) => {
        socket.in('administrator').emit('userChange', user)
    })
})
