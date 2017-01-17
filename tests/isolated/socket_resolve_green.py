__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch(all=True)
    import socket
    import time
    import dns.message
    import dns.query

    n = 10
    delay = 0.01
    addr_map = {'eventlet-test-host{0}.'.format(i): '0.0.0.{0}'.format(i) for i in range(n)}

    def slow_udp(q, *a, **kw):
        addr = addr_map[q.question[0].name.to_text()]
        r = dns.message.make_response(q)
        r.index = None
        r.flags = 256
        r.answer.append(dns.rrset.from_text(str(q.question[0].name), 60, 'IN', 'A', addr))
        r.time = 0.001
        eventlet.sleep(delay)
        return r

    dns.query.udp = slow_udp
    results = {}

    def fun(name):
        try:
            results[name] = socket.gethostbyname(name)
        except socket.error as e:
            print('name: {0} error: {1}'.format(name, e))

    pool = eventlet.GreenPool(size=n + 1)
    t1 = time.time()
    for name in addr_map:
        pool.spawn(fun, name)
    pool.waitall()
    td = time.time() - t1
    assert delay <= td < delay * n, 'Resolve time expected: ~{0}s, real: {1:.3f}'.format(delay, td)
    assert sorted(addr_map.items()) == sorted(results.items())
    print('pass')
