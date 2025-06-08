import machine
try:
    import logic.main as app
    app.main()
except Exception as e:
    machine.reset()
