import sys

import numpy as np
import scipy as sp
import scipy.special as spspecial

import matplotlib.pyplot as plt



def create_random_dataset(n=1000, k=5, sigma=1.0, prior_mu=0.0, prior_sigma=10.0, pi=None):
    if pi == None:
        pi = np.random.multinomial( n, [1./k]*k )
    #c = np.random.randint( 0, k, n )
    X = np.empty( ( n, ) )
    c = np.empty( ( n, ), dtype=int )
    mu = np.random.normal( prior_mu, prior_sigma, k )
    j = 0
    for i,p in enumerate( pi ):
        print i,p
        if p > 0:
            X[ j:j+p ] = np.random.normal( mu[ i ], sigma, p )
            c[ j:j+p ] = i
        j += p
    """for i in xrange( k ):
        c_mask = ( c == i )
        n_c = np.sum( c_mask )
        if n_c > 0:
            X[ c_mask ] = np.random.normal( mu[ i ], sigma, n_c )"""
    return X,c,mu,pi

def normal_scaled_inverse_gamma(mu, sigma, lambd, nu, alpha, beta):
     factor_1 = np.sqrt( nu / ( 2*np.pi ) ) / sigma
     factor_2 = beta ** alpha / spspecial.gamma( alpha )
     factor_3 = ( 1 / sigma**2 ) ** ( alpha + 1 )
     exp_arg = - ( 2 * beta + nu * ( mu - lambd )**2 ) / ( 2 * sigma**2 )
     factor_4 = np.exp( exp_arg )
     return factor_1 * factor_2 * factor_3 * factor_4

def nsig_posterior_hyper_parameters(X, lambd, nu, alpha, beta):
    if type( X ) == np.ndarray:
        N = X.shape[0]
        X_sum = np.sum( X )
        X_mean = X_sum / float( N )
        X_var = np.var( X )
    else:
        N = 1
        X_sum = X
        X_mean = X
        X_var = 0.0
    lambd_p = ( nu * lambd + np.sum( X ) ) / ( nu + N )
    nu_p = nu + N
    alpha_p = alpha + N / 2.0
    beta_p = beta + 0.5 * X_var + N * nu / ( N + nu ) * ( X_mean - lambd )**2 / 2.0
    return lambd_p, nu_p, alpha_p, beta_p

def gaussian(x, mu, sigma):
    return 1 / np.sqrt( 2*np.pi*sigma**2 ) * np.exp( -(x-mu)**2/(2*sigma**2) )

def posterior_class_label(alpha, x, X, c_masks, n_c, mu_c, prior_mu, prior_sigma, model_sigma):
    P = np.empty( ( len( c_masks ) + 1 ), )
    for i, c in enumerate( c_masks ):
        #P[ i ] = n_c[ i ] * posterior_normal( x, X[ c_masks[ i ] ], mu_c[ i ], sigma_0 )
        P[ i ] = n_c[ i ] * posterior_normal( mu_c[ i ], x, prior_mu, prior_sigma, model_sigma )
    mu_p = ( prior_mu/prior_sigma**2 + x/model_sigma**2 ) / ( 1/prior_sigma**2 + 1/model_sigma**2 )
    sigma_p = np.sqrt( ( 1/prior_sigma**2 + 1/model_sigma ** 2 ) ** (-1) )
    v = gaussian( prior_mu, mu_p, np.sqrt( prior_sigma**2 + sigma_p**2 ) )
    """beta = 1 / float( 1 + 1 )
    beta = 1.0
    x = beta * x
    mu_p = 
    sigma_p = np.sqrt( ( 1/prior_sigma**2 + 1/model_sigma ** 2 ) ** (-1) )
    modified_mu = -beta * prior_mu + prior_mu
    modified_sigma = np.sqrt( prior_sigma**2 + sigma_p**2 )
    P[ -1 ] = alpha * gaussian( x, modified_mu, modified_sigma )"""
    P[ -1 ] = alpha * v
    P = P / np.sum( P )
    P_cdf = np.cumsum( P )
    p = np.random.uniform( 0.0, 1.0 )
    choice = -1
    for i,v in enumerate( P_cdf ):
        if p < v:
            choice = i
            break
    #print '\nn_c:', n_c, 'P:', P, 'p:', p
    return choice

    """if choice < c_labels.shape[0]:
        new_c = c_labels[ choice ]
    else:
        new_c = np.max( n_c ) + 1
        new_c_labels = np.empty( ( c_labels.shape[0] + 1, ) )
        new_c_labels[ : -1 ] = c_labels
        new_c_labels[ -1 ] = new_c
        new_mu = posterior_normal( x, mu_0, sigma_0 )
        new_mu_c = np.empty( ( mu_c.shape[0] + 1, ) )
        new_mu_c[ : -1 ] = mu_c
        new_mu_c[ -1 ] = new_mu
        c_labels = new_c_labels
        mu_c = new_mu_c
    return new_c, c_labels, mu_c"""

def posterior_normal(y, X, prior_mu, prior_sigma, model_sigma):
    if type( X ) == np.ndarray:
        mu_p = ( prior_mu/prior_sigma**2 + np.sum(X)/model_sigma**2 ) / ( 1/prior_sigma**2 + X.shape[0]/model_sigma**2 )
        sigma_p = np.sqrt( ( 1/prior_sigma**2 + X.shape[0]/model_sigma ** 2 ) ** (-1) )
    else:
        mu_p = ( prior_mu/prior_sigma**2 + X/model_sigma**2 ) / ( 1/prior_sigma**2 + 1/model_sigma**2 )
        sigma_p = np.sqrt( ( 1/prior_sigma**2 + 1/model_sigma ** 2 ) ** (-1) )
    #print 'mu_p:', mu_p
    #print 'sigma_p:', sigma_p
    return 1 / np.sqrt( 2*np.pi*sigma_p**2 ) * np.exp( - ( y - mu_p )**2 / ( 2*sigma_p**2 ) )

def sample_posterior_normal(X, prior_mu, prior_sigma, model_sigma, size=1):
    if type( X ) == np.ndarray:
        mu_p = ( prior_mu/prior_sigma**2 + np.sum(X)/model_sigma**2 ) / ( 1/prior_sigma**2 + X.shape[0]/model_sigma**2 )
        sigma_p = np.sqrt( ( 1/prior_sigma**2 + X.shape[0]/model_sigma ** 2 ) ** (-1) )
    else:
        mu_p = ( prior_mu/prior_sigma**2 + X/model_sigma**2 ) / ( 1/prior_sigma**2 + 1/model_sigma**2 )
        sigma_p = np.sqrt( ( 1/prior_sigma**2 + 1/model_sigma ** 2 ) ** (-1) )
    return np.random.normal( mu_p, sigma_p, size )

def estimate_dpm_model(alpha, X, iterations=200, prior_mu=0.0, prior_sigma=10.0, model_sigma=1.0, estimated_components=None, iteration_callback=None):
    if estimated_components == None:
        start_N = 1
        #c_labels = range( 0, start_N )
        mu_c = []
        for i in xrange( start_N ):
            mu_c.append( np.random.normal( prior_mu, prior_sigma ) )
            #mu_c.append( sample_posterior_normal( X[ c_masks[ i ] ], prior_mu, prior_sigma )[0] )
    else:
        mu_c = list( estimated_components )
        #c_labels = range( 0, len( mu_c ) )
    c_X = np.random.randint( 0, len( mu_c ), X.shape[0] )
    #max_c_label = np.max( c_labels )
    c_masks = []
    for i in xrange( len( mu_c ) ):
        c_masks.append( c_X == i )
    n_c = []
    for i in xrange( len( mu_c ) ):
        n_c.append( np.sum( c_masks[ i ] ) )

    print 'initial component estimates:'
    print mu_c

    for iter in xrange( iterations ):

        if iter % 1 == 0:
            sys.stdout.write( '\riteration: %d...%d components...' % ( iter, len( mu_c ) ) )
            sys.stdout.flush()

        for i in xrange( X.shape[0] ):
            try:
                n_c[ c_X[ i ] ] -= 1
            except:
                print 'c_X[i]:', c_X[i]
                print ('n_c(%d):' % len(n_c)), n_c
                print 'len(mu_c):', len(mu_c)
                print 'len(c_masks):', len(c_masks)
                raise
            choice = posterior_class_label( alpha, X[ i ], X, c_masks, n_c, mu_c, prior_mu, prior_sigma, model_sigma )
            n_c[ c_X[ i ] ] += 1
            #print 'choice for %f, i=%d: %d' % ( X[ i ], i, choice )
            #print c_X[ i ], n_c[ c_X[ i ] ]
            c_masks[ c_X[ i ] ][ i ] = False
            n_c[ c_X[ i ] ] -= 1
            if choice != c_X[ i ] and n_c[ c_X[ i ] ] == 0:
                print '\ndeleting component %d -> %d components' % ( choice, len( mu_c ) - 1 )
                del n_c[ c_X[ i ] ]
                #del c_labels[ c_X[ i ] ]
                del mu_c[ c_X[ i ] ]
                del c_masks[ c_X[ i ] ]
                mask = c_X >= c_X[ i ]
                c_X[ mask ] -= 1
            if choice < len( mu_c ):
                new_c = choice
                n_c[ choice ] += 1
                c_masks[ choice ][ i ] = True
                c_X[ i ] = choice
            else:
                print '\nadding new component -> %d components' % ( len( mu_c ) + 1 )
                new_mu = sample_posterior_normal( X[ i ], prior_mu, prior_sigma, model_sigma )[0]
                #c_labels.append( max_c_label + 1 )
                #max_c_label += 1
                n_c.append( 1 )
                mu_c.append( new_mu )
                #c_X[ i ] = c_labels[ -1 ]
                c_X[ i ] = choice
                c_masks.append( c_X == choice )
        #M = 0
        for i in xrange( len( mu_c ) ):
            new_mu = sample_posterior_normal( X[ c_masks[ i ] ], prior_mu, prior_sigma, model_sigma )[0]
            mu_c[ i ] = new_mu
            #M += n_c[ i ]
        #print 'M:', M, 'k:', len( mu_c )

        if iteration_callback:
            iteration_callback( mu_c )

        #print 'iterated estimate of components:'
        #print mu_c

    for i in xrange( len( mu_c ) ):
        c_X[ c_masks[ i ] ] = i

    sys.stdout.write( '\n' )
    sys.stdout.flush()

    return c_X, mu_c

N = 1000
K = 5
alpha = 0.01
burn_in_iterations = 50
iterations = 100
prior_mu = 0.0
prior_sigma = 10.0
model_sigma = 1.0

pi = [ 1000., 1500., 2500., 1000., 4000. ]
pi = pi / np.sum( pi ) * N
X, c_X, c_mu, pi = create_random_dataset( N, K, model_sigma, prior_mu, prior_sigma, pi )

print 'mu_0:', c_mu


colors = 'rgbmc'
for i,mu in enumerate( c_mu ):
    A = np.linspace( mu - 10*model_sigma, mu + 10*model_sigma, 100 )
    B = 1/np.sqrt(2*np.pi*model_sigma**2)*np.exp(-(A-mu)**2/(2*model_sigma**2))
    B *= pi[ i ]
    c = colors[ i % len( colors ) ]
    plt.plot( A, B, '%s-' % c )
plt.hist( X, bins=50, alpha=0.5, facecolor='lightgrey' )
plt.show()

# burn-in
estimated_c_X, estimated_c_mu = estimate_dpm_model( alpha, X, burn_in_iterations, prior_mu, prior_sigma, model_sigma )
print 'burn-in estimate:'
print estimated_c_mu

estimated_components = []
def sampler_callback(components):
    estimated_components.append( components )
estimated_c_X, estimated_c_mu = estimate_dpm_model( alpha, X, iterations, prior_mu, prior_sigma, model_sigma, estimated_c_mu, sampler_callback )
mean_number_of_components = 0
for components in estimated_components:
    mean_number_of_components += len( components )
mean_number_of_components /= float( len( estimated_components ) )
mean_number_of_components = int( mean_number_of_components + 0.5 )
print 'mean_number_of_components:', mean_number_of_components
estimated_c_mu = np.zeros( ( mean_number_of_components, ) )
i = 0
for components in estimated_components:
    if len( components ) == mean_number_of_components:
        estimated_c_mu += components
        i += 1
estimated_c_mu /= i

"""mu_p = ( prior_mu + np.sum( X ) ) / prior_sigma**2 / ( ( 1 + X.shape[0] ) / prior_sigma**2 )
sigma_p = np.sqrt( ( ( 1 + X.shape[0] ) / prior_sigma ** 2 ) ** (-1) )
Y = np.linspace( mu_p - 10*sigma_p, mu_p + 10*sigma_p, 100 )
PN = posterior_normal( Y, X, prior_mu, prior_sigma )
Y2 = sample_posterior_normal( X, prior_mu, prior_sigma, 10000 )

plt.plot( Y, PN )
plt.hist( Y2, bins=25, normed=True, alpha=0.5 )
plt.show()"""

print 'real components:'
print c_mu

print 'estimated components:'
print estimated_c_mu

estimated_pi = np.empty( ( estimated_c_mu.shape[0], ) )
for i in xrange( len( estimated_c_mu ) ):
    estimated_pi[ i ] = np.sum( estimated_c_X == i )

colors = 'rgbmc'
for i,mu in enumerate( estimated_c_mu ):
    A = np.linspace( mu - 10*model_sigma, mu + 10*model_sigma, 100 )
    B = 1/np.sqrt(2*np.pi*model_sigma**2)*np.exp(-(A-mu)**2/(2*model_sigma**2))
    B *= estimated_pi[ i ]
    c = colors[ i % len( colors ) ]
    plt.plot( A, B, '%s-' % c )
plt.hist( X, bins=25, alpha=0.5, facecolor='lightgrey' )
plt.show()

